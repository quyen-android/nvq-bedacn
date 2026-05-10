from app.services.rag_service import RagService


print("Số vector:")
print(
    RagService.collection.count()
)

print("\n===================")

data = RagService.collection.get()

print("IDS:")
print(data["ids"])

print("\nDOCUMENTS:")
for doc in data["documents"]:
    print(doc)

print("\n===================")

results = RagService.search_places(
    "quán cafe yên tĩnh view đẹp"
)

print("\nSEARCH RESULT:")
print(results)