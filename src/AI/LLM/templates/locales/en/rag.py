from string import Template

#### RAG PROMPTS ####

system_prompt = Template("\n".join([
    "You are an intelligent AI assistant specialized in analyzing video transcripts and answering user questions about video content.",
    "Your primary function is to help users quickly find and understand information from videos without having to watch them in full.",
    "Always maintain a helpful, informative, and neutral tone.",
    "You have to generate a response based on the documents provided.",
    "You can apologize to the user if you are not able to generate a response.",
]))

document_prompt = Template(
    "\n".join([
        "## Documents",
        "Document No: $doc_num",
        "Content: $chunk_text",
    ])
)

footer_prompt = Template("\n".join([
    "Based only on the above documents"
    "please generate an answer for the user where the video title is $title and its author's name is $author."
    "## Question:",
    "$query",
    "",
    "## Answer:",
]))