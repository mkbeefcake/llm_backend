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
    if not purchased_doc.exists():
        purchased_doc_ref.set({})

    purchased_data = purchased_doc_ref.get().val()

    # if content == "":
    #     pass
    #     # del purchased_data[provider_name][key]
    # else:
    #     updated = []

    #     # iterate original content
    #     try:
    #         for original in purchased_data[provider_name][key]:
    #             # skip statistics item
    #             if "message_id" not in original:
    #                 continue

    #             org_message_id = original["message_id"]
    #             found = False

    #             for newest in content:
    #                 # skip statistics item
    #                 if "message_id" not in newest:
    #                     continue

    #                 new_message_id = newest["message_id"]
    #                 if org_message_id == new_message_id:
    #                     updated.append(newest)
    #                     found = True
    #                     break

    #             if found == False:
    #                 updated.append(original)
    #     except Exception as e:
    #         pass

    #     # iterate new content
    #     try:
    #         for newest in content:
    #             # add new statistics item
    #             if "message_id" not in newest:
    #                 updated.append(newest)
    #                 continue

    #             new_message_id = newest["message_id"]
    #             found = False

    #             for current in updated:
    #                 # skip statistics item
    #                 if "message_id" not in current:
    #                     continue

    #                 current_message_id = current["message_id"]
    #                 if new_message_id == current_message_id:
    #                     found = True
    #                     break

    #             if found == False:
    #                 updated.append(newest)
    #     except Exception as e:
    #         pass

    #     purchased_data[provider_name][key] = updated

    # purchased_doc_ref.update(
    #     {
    #         provider_name: purchased_data[provider_name],
    #     }
    # )
    return {"message": "Purchased data updated successfully"}
