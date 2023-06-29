import json

from db.firebase import db


"""
Here 'key' means 'identifier_name' from frontend
"""


def get_last_message_id(user_id: str, provider_name: str, key: str, chatuser_id: str):
    document_ref = db.collection(
        f"purchased/{user_id}/{provider_name}/{key}/last_message_ids"
    ).document(chatuser_id)
    doc = document_ref.get()
    if not doc.exists:
        document_ref.set({"last_message_id": "0"})

    return document_ref.get().to_dict()["last_message_id"]


def set_last_message_id(
    user_id: str, provider_name: str, key: str, chatuser_id: str, last_message_id: str
):
    document_ref = db.collection(
        f"purchased/{user_id}/{provider_name}/{key}/last_message_ids"
    ).document(chatuser_id)
    document_ref.update({"last_message_id": last_message_id})


def get_last_message_ids(user_id: str, provider_name: str, key: str):
    all_docs = db.collection(
        f"purchased/{user_id}/{provider_name}/{key}/last_message_ids"
    ).get()

    content = {}
    for doc in all_docs:
        content[doc.id] = doc.to_dict()
    return content


def create_purchased(user_id: str):
    document_ref = db.collection("purchased").document(user_id)
    document_ref.set({})
    return {"message": "Purchased created successfully"}


def update_purchased(user_id: str, provider_name: str, key: str, new_content: any):
    document_ref = db.collection(f"purchased/{user_id}/{provider_name}").document(key)
    doc = document_ref.get()
    if not doc.exists:
        document_ref.set({})

    original_data = document_ref.get().to_dict()

    if new_content == None or new_content == "":
        pass
        # del original_data[provider_name][key]
    else:
        # iterate all chat users from original
        for chatuser_id in original_data:
            # get last_message_id
            last_message_id = get_last_message_id(
                user_id, provider_name, key, chatuser_id
            )

            # update statistic
            if chatuser_id in new_content and "statistics" in new_content[chatuser_id]:
                original_data[chatuser_id]["statistics"] = new_content[chatuser_id][
                    "statistics"
                ]

            # update purchased
            if chatuser_id in new_content and "purchased" in new_content[chatuser_id]:
                original_purchased = original_data[chatuser_id]["purchased"]
                newest_purchased = new_content[chatuser_id]["purchased"]

                updated = []

                # iterate original purchased
                try:
                    for original in original_purchased:
                        org_message_id = original["message_id"]
                        found = False

                        for newest in newest_purchased:
                            new_message_id = newest["message_id"]
                            if org_message_id == new_message_id:
                                updated.append(newest)
                                found = True
                                break

                        if found == False:
                            updated.append(original)
                except Exception as e:
                    pass

                # iterate new purchased
                try:
                    for newest in newest_purchased:
                        new_message_id = newest["message_id"]
                        found = False

                        for current in updated:
                            current_message_id = current["message_id"]
                            if new_message_id == current_message_id:
                                found = True
                                break

                        if found == False:
                            updated.append(newest)
                            if int(last_message_id) < int(new_message_id):
                                last_message_id = new_message_id

                except Exception as e:
                    pass

                original_data[chatuser_id]["purchased"] = updated

            # update last_message_id
            set_last_message_id(
                user_id, provider_name, key, chatuser_id, last_message_id
            )

        # iterate all chat users from new_content
        for chatuser_id in new_content:
            if chatuser_id not in original_data:
                # add new content
                original_data[chatuser_id] = new_content[chatuser_id]

                # get last_message_id
                last_message_id = get_last_message_id(
                    user_id, provider_name, key, chatuser_id
                )

                if "purchased" not in new_content[chatuser_id]:
                    continue

                newest_purchased = new_content[chatuser_id]["purchased"]
                try:
                    for newest in newest_purchased:
                        new_message_id = newest["message_id"]
                        if int(last_message_id) < int(new_message_id):
                            last_message_id = new_message_id

                except Exception as e:
                    pass

                # update last_message_id
                set_last_message_id(
                    user_id, provider_name, key, chatuser_id, last_message_id
                )

        document_ref.update(original_data)
    return {"message": "Purchased data updated successfully"}
