def retrieve_docs(db, query, k=8):

    retriever = db.as_retriever( 
        search_type="similarity",
        search_kwargs={"k": k}
    )

    return retriever.invoke(query)