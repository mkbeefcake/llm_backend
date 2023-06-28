import json

from db.firebase import db


def create_purchased(user_id: str):
    purchased_doc_ref = db.collection("purchased").document(user_id)
    purchased_doc_ref.set({})
    return {"message": "Purchased created successfully"}


def update_purchased(user_id: str, provider_name: str, key: str, content: any):
    purchased_doc_ref = db.collection("purchased").document(user_id)
    purchased_data = get_purchased_data(user_id)

    if not purchased_data:
        create_purchased(user_id=user_id)
        purchased_data = {}

    if not provider_name in purchased_data:
        purchased_data[provider_name] = {}

    if not key in purchased_data[provider_name]:
        purchased_data[provider_name][key] = {}

    if content == "":
        pass
        # del purchased_data[provider_name][key]
    else:
        updated = []

        # iterate original content
        try:
            for original in purchased_data[provider_name][key]:
                org_message_id = original["message_id"]
                found = False

                for newest in content:
                    new_message_id = newest["message_id"]
                    if org_message_id == new_message_id:
                        updated.append(newest)
                        found = True
                        break

                if found == False:
                    updated.append(original)
        except Exception as e:
            pass

        # iterate new content
        try:
            for newest in content:
                new_message_id = newest["message_id"]
                found = False

                for current in updated:
                    current_message_id = current["message_id"]
                    if new_message_id == current_message_id:
                        found = True
                        break

                if found == False:
                    updated.append(newest)
        except Exception as e:
            pass

        purchased_data[provider_name][key] = updated

    purchased_doc_ref.update(
        {
            provider_name: purchased_data[provider_name],
        }
    )
    return {"message": "Purchased data updated successfully"}


def get_purchased_data(id: str):
    purchased_doc_ref = db.collection("purchased").document(id)
    purchased_doc = purchased_doc_ref.get()
    if purchased_doc.exists:
        purchased_data = purchased_doc.to_dict()
        return purchased_data
    else:
        return None
