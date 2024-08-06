from flask_restful import Resource, reqparse
from ..database import get_db
from ..models import Conversation
from .openai_api import client

class ConversationResource(Resource):
    @staticmethod
    def summarize_user_query(user_query):
        prompt = f"Summarize this query in 3-4 words: '{user_query}'. Only return the summarization, do not explain anything."
        messages = [{"role": "user", "content": prompt}]
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages
        )
        summary = completion.choices[0].message.content.strip()
        return summary

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False, help="Conversation ID")
        args = parser.parse_args()

        conversation_id = args.get('id')
        with get_db() as db:
            if conversation_id:
                conversation = db.query(Conversation).filter_by(id=conversation_id).first()
                if conversation:
                    return {
                        "id": conversation.id,
                        "user_query_summary": conversation.user_query_summary,
                        "user_query": conversation.user_query,
                        "retrieved_data": conversation.retrieved_data,
                        "model_response": conversation.model_response,
                        "date_time": conversation.date_time,
                        "query_status": conversation.query_status
                    }, 200
                else:
                    return {"error": "Conversation not found"}, 404
            else:
                conversations = db.query(Conversation).all()
                conversations_list = [
                    {
                        "id": conv.id,
                        "user_query_summary": conv.user_query_summary,
                        "date_time": conv.date_time
                    } for conv in conversations
                ]
                return {"conversations": conversations_list}, 200

    def delete(self, id):
        with get_db() as db:
            conversation = db.query(Conversation).filter_by(id=id).first()
            if conversation:
                db.delete(conversation)
                db.commit()
                return {"message": "Conversation deleted successfully"}, 200
            else:
                return {"error": "Conversation not found"}, 404
