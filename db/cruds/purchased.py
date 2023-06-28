import json

from db.firebase import db


def create_purchased(user_id: str):
    purchased_doc_ref = db.collection("purchased").document(user_id)
    purchased_doc_ref.set({})
    return {"message": "Purchased created successfully"}


def update_purchased(user_id: str, provider_name: str, key: str, content: any):
    purchased_doc_ref = db.collection(f"purchased/{user_id}/{provider_name}").document(
        key
    )
    purchased_doc = purchased_doc_ref.get()
    if not purchased_doc.exists:
        purchased_doc_ref.set({})

    purchased_data = purchased_doc_ref.get().to_dict()

    if content == None or content == "":
        pass
        # del purchased_data[provider_name][key]
    else:
        # iterate original content
        for chatuser_id in purchased_data:
            if chatuser_id in content and "statistics" in content[chatuser_id]:
                purchased_data[chatuser_id]["statistics"] = content[chatuser_id][
                    "statistics"
                ]

            if chatuser_id in content and "purchased" in content[chatuser_id]:
                original_content = purchased_data[chatuser_id]["purchased"]
                newest_content = content[chatuser_id]["purchased"]

                updated = []

                # iterate original content
                try:
                    for original in original_content:
                        org_message_id = original["message_id"]
                        found = False

                        for newest in newest_content:
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
                    for newest in newest_content:
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

                purchased_data[chatuser_id]["purchased"] = updated

        for chatuser_id in content:
            if chatuser_id not in purchased_data:
                purchased_data[chatuser_id] = content[chatuser_id]

        purchased_doc_ref.update(purchased_data)
    return {"message": "Purchased data updated successfully"}
