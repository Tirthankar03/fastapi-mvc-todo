# from fastapi import FastAPI
# from routes.todo_routes import router

# app = FastAPI()
# app.include_router(router)

#######################################################



# from fastapi import FastAPI, UploadFile, HTTPException
# from google.generativeai import GenerativeModel, configure
# import os

# app = FastAPI()

# # Configure Gemini API with your API key
# # Replace 'YOUR_API_KEY' with your actual Gemini API key
# configure(api_key='AIzaSyBCv6jRQctk9DVdJ62d1dBreuqPptwMdFg')

# # Initialize the Gemini 2.0 Flash model
# model = GenerativeModel('gemini-2.0-flash')

# @app.post("/analyze-resume/")
# async def analyze_resume(file: UploadFile):
#     try:
#         # Check if file is PDF
#         if not file.filename.endswith('.pdf'):
#             raise HTTPException(status_code=400, detail="Please upload a PDF file")
        
#         # Read the PDF file content
#         pdf_content = await file.read()
        
#         # Prepare the prompt for Gemini
#         prompt = "Analyze this resume PDF and extract all personal and professional details including name, contact information, education, work experience, skills, and any other relevant information. Return the details in a structured format."
        
#         # Send the PDF directly to Gemini along with the prompt
#         # Note: Gemini API might have specific requirements for handling raw PDF bytes
#         response = model.generate_content(
#             [prompt, {"mime_type": "application/pdf", "data": pdf_content}]
#         )
        
#         # Get the response text
#         resume_details = response.text
        
#         return {
#             "status": "success",
#             "resume_details": resume_details
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

# Run the app with: uvicorn filename:app --reload


# from fastapi import FastAPI, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse
# from google.generativeai import GenerativeModel, configure
# from pydantic import BaseModel

# app = FastAPI()


# class SyllabusSchema(BaseModel):
#     chapter_no: str
#     chapter_name: str
#     chapter: str

# # Configure Gemini
# configure(api_key='AIzaSyBCv6jRQctk9DVdJ62d1dBreuqPptwMdFg')

# # Initialize the Gemini Flash model
# model = GenerativeModel('gemini-2.0-flash')

# @app.post("/extract-syllabus/")
# async def extract_syllabus(
#     file: UploadFile,
#     custom_prompt: str = Form(default="")
# ):
#     try:
#         # Validate PDF
#         if not file.filename.lower().endswith('.pdf'):
#             raise HTTPException(status_code=400, detail="Please upload a PDF file.")

#         pdf_content = await file.read()

#         # Base system prompt
#         system_prompt = (
#             "You are a helpful assistant. Extract chapter information from this syllabus PDF.\n"
#             "Return a JSON array, where each object contains:\n"
#             "- chapter_no (assign one if not mentioned)\n"
#             "- chapter_name\n"
#             "- weightage (null if not mentioned)\n"
#             "Be accurate, and keep output clean and structured."
#         )

#         # Merge with custom prompt if provided
#         full_prompt = system_prompt + "\n\nAdditional instructions:\n" + custom_prompt if custom_prompt else system_prompt

#         # Send to Gemini with prompt + PDF
#         response = model.generate_content([
#             full_prompt,
#             {"mime_type": "application/pdf", "data": pdf_content}
#         ])

#         return {
#             "status": "success",
#             "output": response.text
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")



from fastapi import FastAPI, UploadFile, Form, HTTPException, File
from fastapi.responses import JSONResponse
from google.generativeai import GenerativeModel, configure, embed_content
import google.generativeai as genai
from pydantic import BaseModel
from docling.document_converter import DocumentConverter, DocumentStream
from io import BytesIO
import tempfile
import os
import json
from typing import List, Optional
from config.supabase import supabase
from uuid import UUID
import fitz  # PyMuPDF
# from google.generativeai import GenerativeModel, configure, embed_content

app = FastAPI(redirect_slashes=False)
converter = DocumentConverter()



class SyllabusSchema(BaseModel):
    chapter_no: str
    chapter_name: str
    chapter: str


# Configure Gemini
configure(api_key='AIzaSyBCv6jRQctk9DVdJ62d1dBreuqPptwMdFg')

# Initialize the Gemini Flash model
model = GenerativeModel('gemini-2.0-flash')
genai.configure(api_key='AIzaSyBCv6jRQctk9DVdJ62d1dBreuqPptwMdFg')

@app.post("/extract-syllabus")
async def extract_syllabus(
    file: UploadFile,
    custom_prompt: str = Form(default="")
):
    try:
        # Validate PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Please upload a PDF file.")

        pdf_content = await file.read()
        # Base system prompt
        # system_prompt = (
        #     "You are a helpful assistant. Extract chapter information from this syllabus PDF.\n"
        #     "Return a JSON array, where each object contains:\n"
        #     "- chapter_no (assign one if not mentioned)\n"
        #     "- chapter_name\n"
        #     "Be accurate, and keep output clean and structured."
        # )

        system_prompt = (
            "You are an expert academic assistant. Extract chapter information from this syllabus PDF.\n"
            "Return only a clean JSON array of strings, where each string is a chapter title. Example:\n\n"
            "[\"Chapter 1\", \"Chapter 2\", \"Chapter 3\"]"
        )

        # Merge with custom prompt if provided
        full_prompt = system_prompt + "\n\nAdditional instructions:\n" + custom_prompt if custom_prompt else system_prompt

        # Send to Gemini with prompt + PDF
        response = model.generate_content([
            full_prompt,
            {"mime_type": "application/pdf", "data": pdf_content}
        ])

        # Parse the response text into a Python object (list of dicts)
        try:
            # Remove any potential markdown or extra formatting (e.g., ```json)
            cleaned_response = response.text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:-3].strip()  # Remove ```json and ```
            syllabus_data = json.loads(cleaned_response)  # Convert JSON string to Python object
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse model response as JSON: {str(e)}")

        # Return the parsed data as a proper JSON response
        return JSONResponse(content={
            "status": "success",
            "output": syllabus_data
        })


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    


# 1 - add chapters to supabase

@app.post("/add-chapters-to-base")
async def add_chapters_to_base(
    subject: str = Form(...),
    class_: str = Form(..., alias="class"),
    chapters: str = Form(...)
):
    try:
        # Parse the chapters string to a Python list
        chapter_list = json.loads(chapters)
        if not isinstance(chapter_list, list):
            raise ValueError("Chapters must be a JSON list.")

        inserts = []
        for chapter in chapter_list:
            inserts.append({
                "class": class_,
                "subject": subject,
                "chapter": chapter
            })

        response = supabase.table("base").insert(inserts).execute()

        return JSONResponse(content={
            "status": "success",
            "inserted": len(inserts),
            "data": response.data
            # "data": inserts
        })

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for chapters.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/extract-markdown")
async def extract_markdown(
    file: UploadFile,
    custom_prompt: str = Form(default="")
):
    try:
        # Validate PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Please upload a PDF file.")

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            pdf_content = await file.read()
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name

        # Convert using file path
        result = converter.convert(temp_file_path)
        document = result.document
        markdown_output = document.export_to_markdown()

        # Clean up
        os.unlink(temp_file_path)

        return JSONResponse(content={
            "status": "success",
            "output": markdown_output
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    


# Custom embedding function using Gemini
class GeminiEmbeddingFunction:
    def compute_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = genai.embed_content(model="models/embedding-001", content=text)
            embeddings.append(response["embedding"])
        return embeddings

    def ndims(self) -> int:
        return 768  # Dimensions for Gemini embeddings


gemini_func = GeminiEmbeddingFunction()




# extract subtopics + summary (2 LLM)

@app.post("/extract-subtopics")
async def extract_subtopics(
    file: UploadFile,
    custom_prompt: str = Form(default="")
):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Please upload a PDF file.")

        pdf_content = await file.read()

        # ======================
        # Step 1: Extract subtopics
        # ======================
        step1_prompt = (
            "You are an expert academic assistant. Extract important subtopics from this chapter PDF" \
            "These subtopics should represent meaningful concepts or learning objectives—not just headings"
            "Return only a clean JSON array of strings, where each string is a subtopic title. Example:\n\n"
            "[\"Subtopic 1\", \"Subtopic 2\", \"Subtopic 3\"]"
        )

        if custom_prompt:
            step1_prompt += f"\n\nAdditional Instructions:\n{custom_prompt}"

        response1 = model.generate_content([
            step1_prompt,
            {"mime_type": "application/pdf", "data": pdf_content}
        ])
        raw_subtopics = response1.text.strip()
        if raw_subtopics.startswith("```json"):
            raw_subtopics = raw_subtopics[7:-3].strip()
        subtopic_titles = json.loads(raw_subtopics)

        # ======================
        # Step 2: Summarize each subtopic (in one call)
        # ======================
        step2_prompt = (
            "Given the following list of subtopics and the chapter PDF, write a 6-7 line summary for each subtopic. "
            "Return the output as a JSON object with subtopics as keys and their summaries as values. Example:\n\n"
            "{\n"
            "  \"Subtopic 1\": \"...summary...\",\n"
            "  \"Subtopic 2\": \"...summary...\"\n"
            "}"
        )
        step2_prompt += f"\n\nSubtopics:\n{subtopic_titles}"

        response2 = model.generate_content([
            step2_prompt,
            {"mime_type": "application/pdf", "data": pdf_content}
        ])
        raw_summary = response2.text.strip()
        if raw_summary.startswith("```json"):
            raw_summary = raw_summary[7:-3].strip()
        summary_dict = json.loads(raw_summary)

        # ======================
        # Step 3: Embed summaries
        # ======================
        summaries = [summary_dict[sub] for sub in subtopic_titles]

        # Final structured output
        final = []
        for idx, subtopic in enumerate(subtopic_titles):
            final.append({
                "subtopic": subtopic,
                "summary": summaries[idx]
            })

        return JSONResponse(content={
            "status": "success",
            "subtopics": final
        })

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# extract subtopics + summary + embeddings
@app.post("/extract-subtopics-embeddings")
async def extract_subtopics_embeddings(
    file: UploadFile,
    custom_prompt: str = Form(default="")
):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Please upload a PDF file.")

        pdf_content = await file.read()

        # ======================
        # Step 1: Extract subtopics
        # ======================
        step1_prompt = (
            "You are an expert academic assistant. Extract important subtopics from this chapter PDF. "
            "These subtopics should represent meaningful concepts or learning objectives—not just headings. "
            "Return only a clean JSON array of strings, where each string is a subtopic title. Example:\n\n"
            "[\"Subtopic 1\", \"Subtopic 2\", \"Subtopic 3\"]"
        )

        if custom_prompt:
            step1_prompt += f"\n\nAdditional Instructions:\n{custom_prompt}"

        response1 = model.generate_content([
            step1_prompt,
            {"mime_type": "application/pdf", "data": pdf_content}
        ])
        raw_subtopics = response1.text.strip()
        if raw_subtopics.startswith("```json"):
            raw_subtopics = raw_subtopics[7:-3].strip()
        subtopic_titles = json.loads(raw_subtopics)

        # ======================
        # Step 2: Summarize each subtopic (in one call)
        # ======================
        step2_prompt = (
            "Given the following list of subtopics and the chapter PDF, write a 6-7 line summary for each subtopic. "
            "Return the output as a JSON object with subtopics as keys and their summaries as values. Example:\n\n"
            "{\n"
            "  \"Subtopic 1\": \"...summary...\",\n"
            "  \"Subtopic 2\": \"...summary...\"\n"
            "}"
        )
        step2_prompt += f"\n\nSubtopics:\n{subtopic_titles}"

        response2 = model.generate_content([
            step2_prompt,
            {"mime_type": "application/pdf", "data": pdf_content}
        ])
        raw_summary = response2.text.strip()
        if raw_summary.startswith("```json"):
            raw_summary = raw_summary[7:-3].strip()
        summary_dict = json.loads(raw_summary)

        # ======================
        # Step 3: Embed subtopic + summary
        # ======================
        combined_texts = [
            f"{subtopic}: {summary_dict[subtopic]}" for subtopic in subtopic_titles
        ]
        embeddings = gemini_func.compute_embeddings(combined_texts)

        # Final structured output
        final = []
        for idx, subtopic in enumerate(subtopic_titles):
            final.append({
                "subtopic": subtopic,
                "summary": summary_dict[subtopic],
                "embedding": embeddings[idx]
            })

        return JSONResponse(content={
            "status": "success",
            "subtopics": final
        })

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



class SubtopicEntry(BaseModel):
    subtopic: str
    summary: str


class SubtopicList(BaseModel):
    subtopics: List[SubtopicEntry]

# get embeddings for subtopics: [{subtopic, summary}]
@app.post("/generate-subtopic-embeddings")
async def generate_subtopic_embeddings(payload: SubtopicList):
    try:
        # Step 1: Combine subtopic and summary for better embedding context
        combined_texts = [
            f"{entry.subtopic}: {entry.summary}" for entry in payload.subtopics
        ]

        # Step 2: Generate embeddings using Gemini
        embeddings = gemini_func.compute_embeddings(combined_texts)

        # Step 3: Append embedding to each entry
        results = []
        for idx, entry in enumerate(payload.subtopics):
            results.append({
                "subtopic": entry.subtopic,
                "summary": entry.summary,
                "embedding": embeddings[idx]
            })

        return JSONResponse(content={
            "status": "success",
            "subtopics": results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    


class StoreRequest(BaseModel):
    base_id: str
    subtopics: List[SubtopicEntry]


@app.post("/store-subtopics")
async def store_subtopics(payload: StoreRequest):
    try:
        # Step 1: Combine subtopic and summary for embedding
        combined = [f"{item.subtopic}: {item.summary}" for item in payload.subtopics]
        embeddings = gemini_func.compute_embeddings(combined)

        # Step 2: Prepare rows for insertion
        rows = []
        for i, (entry, embedding) in enumerate(zip(payload.subtopics, embeddings)):
            rows.append({
                "base_id": payload.base_id,
                "order_in_chapter": i + 1,
                "subtopic": entry.subtopic,
                "description": entry.summary,
                "embedding": embedding
            })

        # Step 3: Insert into expanded_syllabus table
        response = supabase.table("expanded_syllabus").insert(rows).execute()

        print("response in expanded_syllabus>>>", response)

        return {
            "status": "success",
            "inserted_count": len(rows),
            "message": "Subtopics stored in Expanded_Syllabus"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

class QuestionMatchRequest(BaseModel):
    question: str
    marks: int  # Optional, for future use


@app.post("/match-question")
async def match_question_pgvector(payload: QuestionMatchRequest):
    try:
        # Step 1: Get the question embedding
        question_embedding = gemini_func.compute_embeddings([payload.question])[0]

        # # Step 2: Use pgvector query with <=> (cosine distance) in Supabase
        # query = f"""
        #     SELECT subtopic, description, 1 - (embedding <=> ARRAY{question_embedding}) AS similarity
        #     FROM "expanded_syllabus"
        #     ORDER BY embedding <=> ARRAY{question_embedding}
        #     LIMIT 3;
        # """

        # response = supabase.rpc("sql", {"q": query}).execute()
        response = supabase.rpc("match_question_vector", {
            "input_embedding": question_embedding
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No matches found.")

        top_matches = [
            {
                "id": row["id"],
                "subtopic": row["subtopic"],
                "description": row["description"],
                "similarity_percentage": round(row["similarity"] * 100, 2)
            }
            for row in response.data
        ]

        return {
            "status": "success",
            "question": payload.question,
            "top_matches": top_matches
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# @app.post("/extract-questions")
# async def extract_questions_from_pdf(
#     question_paper: UploadFile = File(...),
#     custom_prompt: Optional[str] = Form(None)
# ):
#     try:
#         # Step 1: Extract raw text from PDF
#         content = await question_paper.read()
#         doc = fitz.open(stream=content, filetype="pdf")
#         text = ""
#         img_hints = []

#         for i, page in enumerate(doc):
#             text += page.get_text()
#             if page.get_images(full=True):  # detect if images are on this page
#                 img_hints.append(i)

#         # Step 2: Construct the system prompt for the LLM
#         base_prompt = """
#         Extract all the questions from the following question paper text. 
#         For each question, identify the question text, its marks, and the section if applicable.
#         If a question is associated with an image (figure, diagram, map etc.), include "imgUrl": "1".
#         Return the result in the following JSON format:
#         [
#             {"question": "...", "marks": "..."},
#             {"question": "...", "marks": "...", "imgUrl": "1"}
#         ]
#         Only include valid questions and ensure formatting is consistent.
#         """

#         prompt = f"{custom_prompt}\n\n{text}" if custom_prompt else f"{base_prompt}\n\n{text}"

#         # Step 3: Use the Gemini model
#         response = model.generate_content(prompt)
#         extracted_data = response.text.strip()

#         # Optional: Clean up any markdown-style code block like ```json
#         if extracted_data.startswith("```json"):
#             extracted_data = extracted_data[7:-3].strip()

#         parsed_data = json.loads(extracted_data)

#         # Step 4: Return structured JSON
#         return JSONResponse(content={
#             "status": "success",
#             "data": parsed_data
#         })

#     except json.JSONDecodeError as e:
#         return JSONResponse(status_code=500, content={"status": "error", "message": f"JSON parse error: {str(e)}"})
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})



@app.post("/extract-questions")
async def extract_questions_from_pdf(
    question_paper: UploadFile = File(...),
    custom_prompt: Optional[str] = Form(None)
):
    try:
        # Step 1: Extract raw text from PDF
        content = await question_paper.read()
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        img_hints = []

        for i, page in enumerate(doc):
            text += page.get_text()
            if page.get_images(full=True):
                img_hints.append(i)

        # Step 2: Construct the system prompt for the LLM
        #2
        # base_prompt = """
        # Extract all the questions from the following question paper text, adhering to its sectional structure: 
        # - Section A: Questions 1 to 20 are Multiple Choice Questions (MCQs), each worth 1 mark.
        # - Section B: Questions 21 to 24 are Very Short Answer questions, each worth 2 marks.
        # - Section C: Questions 25 to 29 are Short Answer questions, each worth 3 marks.
        # - Section D: Questions 30 to 33 are Long Answer questions, each worth 5 marks.
        # - Section E: Questions 34 to 36 are Case-based/Source-based questions, each with sub-questions, totaling 4 marks per question.
        # - Section F: Question 37 is a Map skill-based question with parts, totaling 5 marks.

        # For each question, follow these rules:
        # 1. **Question Text**: 
        #    - Include the full question text. For MCQs, include the question and all options (e.g., (A), (B), (C), (D)). 
        #    - For Section E, include the entire source passage and all sub-questions (e.g., 34.1, 34.2, 34.3) as one question.
        #    - For Section F, include the entire question with all parts (e.g., 37(a) and 37(b)) as one question.
        # 2. **Marks**: 
        #    - Provide the total marks as a single number (e.g., "5" instead of "2+3=5") based on the section's mark scheme.
        #    - For Section E, each question (34, 35, 36) has a total of 4 marks.
        #    - For Section F, question 37 has a total of 5 marks.
        # 3. **Image Association**: 
        #    - Include "imgUrl": "1" if the question mentions "picture", "figure", "diagram", "map", or similar terms indicating a visual element.
        #    - For Section F (map-based), always include "imgUrl": "1".
        # 4. **Exclusions**: 
        #    - Ignore instructions, notes, or alternative questions for visually impaired candidates.
        #    - Ignore text in languages other than English.

        # Return the result in this JSON format:
        # [
        #     {"question": "...", "marks": "..."},
        #     {"question": "...", "marks": "...", "imgUrl": "1"}
        # ]
        # Ensure all numbered questions (1 to 37) are extracted with consistent formatting and accurate marks.
        # """
        #3
        # base_prompt = """
        # Extract all the questions from the following question paper text, adhering to its sectional structure: 
        # - Section A: Questions 1 to 20 are Multiple Choice Questions (MCQs), each worth 1 mark.
        # - Section B: Questions 21 to 24 are Very Short Answer questions, each worth 2 marks.
        # - Section C: Questions 25 to 29 are Short Answer questions, each worth 3 marks.
        # - Section D: Questions 30 to 33 are Long Answer questions, each worth 5 marks.
        # - Section E: Questions 34 to 36 are Case-based/Source-based questions, each with sub-questions, totaling 4 marks per question.
        # - Section F: Question 37 is a Map skill-based question with parts, totaling 5 marks.

        # For each question, follow these rules:
        # 1. **Question Text**: 
        #    - Include the full question text. For MCQs, include the question and all options (e.g., (A), (B), (C), (D)). 
        #    - For questions with "OR" options (e.g., (a) OR (b)), treat each option as a separate question with its own entry in the output.
        #    - For Section E, include the entire source passage and all sub-questions (e.g., 34.1, 34.2, 34.3) as one question.
        #    - For Section F, include the entire question with all parts (e.g., 37(a) and 37(b)) as one question.
        # 2. **Marks**: 
        #    - Provide the total marks as a single number (e.g., "5" instead of "2+3=5") based on the section's mark scheme.
        #    - For Section B, each question (including OR options) has 2 marks.
        #    - For Section C, each question (including OR options) has 3 marks.
        #    - For Section D, each question (including OR options) has 5 marks.
        #    - For Section E, each question (34, 35, 36) has a total of 4 marks.
        #    - For Section F, question 37 has a total of 5 marks.
        # 3. **Image Association**: 
        #    - Include "imgUrl": "1" if the question mentions "picture", "figure", "diagram", "map", or similar terms indicating a visual element.
        #    - For Section F (map-based), always include "imgUrl": "1".
        # 4. **Exclusions**: 
        #    - Ignore instructions, notes, or alternative questions for visually impaired candidates.
        #    - Ignore text in languages other than English.

        # Return the result in this JSON format:
        # [
        #     {"question": "...", "marks": "..."},
        #     {"question": "...", "marks": "...", "imgUrl": "1"}
        # ]
        # Ensure all numbered questions (1 to 37, including separate OR options) are extracted with consistent formatting and accurate marks.
        # """
        #4
        # base_prompt = """
        # Extract all the questions from the following question paper text, adhering to its sectional structure: 
        # - Section A: Questions 1 to 20 are Multiple Choice Questions (MCQs), each worth 1 mark.
        # - Section B: Questions 21 to 24 are Very Short Answer questions, each worth 2 marks.
        # - Section C: Questions 25 to 29 are Short Answer questions, each worth 3 marks.
        # - Section D: Questions 30 to 33 are Long Answer questions, each worth 5 marks.
        # - Section E: Questions 34 to 36 are Case-based/Source-based questions, each with sub-questions, totaling 4 marks per question.
        # - Section F: Question 37 is a Map skill-based question with parts, totaling 5 marks.

        # For each question, follow these rules:
        # 1. **Question Text**: 
        #    - Include the full question text. For MCQs, include the question and all options (e.g., (A), (B), (C), (D)). 
        #    - For questions with "OR" options (e.g., (a) OR (b)), treat each option as a separate question with its own entry in the output.
        #    - Remove any "(a)" or "(b)" prefixes from the question text to ensure a clean format (e.g., "How did the Silk Route connect the world ?" instead of "(a) How did the Silk Route connect the world ?").
        #    - For Section E, include the entire source passage and all sub-questions (e.g., 34.1, 34.2, 34.3) as one question.
        #    - For Section F, include the entire question with all parts (e.g., 37(a) and 37(b)) as one question.
        # 2. **Marks**: 
        #    - Provide the total marks as a single number (e.g., "5" instead of "2+3=5") based on the section's mark scheme.
        #    - For Section B, each question (including OR options) has 2 marks.
        #    - For Section C, each question (including OR options) has 3 marks.
        #    - For Section D, each question (including OR options) has 5 marks.
        #    - For Section E, each question (34, 35, 36) has a total of 4 marks.
        #    - For Section F, question 37 has a total of 5 marks.
        # 3. **Image Association**: 
        #    - Include "imgUrl": "1" if the question mentions "picture", "figure", "diagram", or similar terms indicating a visual element (except for map-based questions).
        #    - For Section F (map-based), always include "imgUrl": "2".
        # 4. **Exclusions**: 
        #    - Ignore instructions, notes, or alternative questions for visually impaired candidates.
        #    - Ignore text in languages other than English.

        # Return the result in this JSON format:
        # [
        #     {"question": "...", "marks": "..."},
        #     {"question": "...", "marks": "...", "imgUrl": "1"},
        #     {"question": "...", "marks": "...", "imgUrl": "2"}
        # ]
        # Ensure all numbered questions (1 to 37, including separate OR options) are extracted with consistent formatting and accurate marks.
        # """

        #5
        # base_prompt = """
        # Extract all the questions from the following question paper text, adhering to its sectional structure: 
        # - Section A: Questions 1 to 20 are Multiple Choice Questions (MCQs), each worth 1 mark.
        # - Section B: Questions 21 to 24 are Very Short Answer questions, each worth 2 marks.
        # - Section C: Questions 25 to 29 are Short Answer questions, each worth 3 marks.
        # - Section D: Questions 30 to 33 are Long Answer questions, each worth 5 marks.
        # - Section E: Questions 34 to 36 are Case-based/Source-based questions, each with sub-questions, totaling 4 marks per question.
        # - Section F: Question 37 is a Map skill-based question with parts, totaling 5 marks.

        # For each question, follow these rules:
        # 1. **Question Text**: 
        #    - For Section A (MCQs, questions 1 to 20), include the full question text with the stem and all options (e.g., (A), (B), (C), (D)) in a single entry. Do not extract incomplete MCQs (e.g., question stem without options) or create duplicate entries.
        #    - For questions with "OR" options (e.g., (a) OR (b)), treat each option as a separate question with its own entry in the output.
        #    - Remove any "(a)" or "(b)" prefixes from the question text to ensure a clean format (e.g., "How did the Silk Route connect the world ?" instead of "(a) How did the Silk Route connect the world ?").
        #    - For Section E, include the entire source passage and all sub-questions (e.g., 34.1, 34.2, 34.3) as one question.
        #    - For Section F, include the entire question with all parts (e.g., 37(a) and 37(b)) as one question.
        # 2. **Marks**: 
        #    - Provide the total marks as a single number (e.g., "5" instead of "2+3=5") based on the section's mark scheme.
        #    - For Section A, each MCQ has 1 mark.
        #    - For Section B, each question (including OR options) has 2 marks.
        #    - For Section C, each question (including OR options) has 3 marks.
        #    - For Section D, each question (including OR options) has 5 marks.
        #    - For Section E, each question (34, 35, 36) has a total of 4 marks.
        #    - For Section F, question 37 has a total of 5 marks.
        # 3. **Image Association**: 
        #    - Include "imgUrl": "1" if the question mentions "picture", "figure", "diagram", or similar terms indicating a visual element (except for map-based questions).
        #    - For Section F (map-based), always include "imgUrl": "2".
        # 4. **Exclusions**: 
        #    - Ignore instructions, notes, or alternative questions for visually impaired candidates.
        #    - Ignore text in languages other than English.

        # Return the result in this JSON format:
        # [
        #     {"question": "...", "marks": "..."},
        #     {"question": "...", "marks": "...", "imgUrl": "1"},
        #     {"question": "...", "marks": "...", "imgUrl": "2"}
        # ]
        # Ensure all numbered questions (1 to 37, including separate OR options) are extracted with consistent formatting, accurate marks, and no duplicate entries. For Section A, ensure exactly 20 MCQs are extracted, each with its full question text and options.
        # """
        #6
        # base_prompt = """
        # Extract all the questions from the following question paper text, adhering to its sectional structure: 
        # - Section A: Questions 1 to 20 are Multiple Choice Questions (MCQs), each worth 1 mark.
        # - Section B: Questions 21 to 24 are Very Short Answer questions, each worth 2 marks.
        # - Section C: Questions 25 to 29 are Short Answer questions, each worth 3 marks.
        # - Section D: Questions 30 to 33 are Long Answer questions, each worth 5 marks.
        # - Section E: Questions 34 to 36 are Case-based/Source-based questions, each with sub-questions, totaling 4 marks per question.
        # - Section F: Question 37 is a Map skill-based question with parts, totaling 5 marks.

        # For each question, follow these rules:
        # 1. **Question Text**: 
        #    - For Section A (MCQs, questions 1 to 20), include the full question text with the stem and all options (e.g., (A), (B), (C), (D)) in a single entry. Do not extract incomplete MCQs (e.g., question stem without options) or create duplicate entries.
        #    - For questions with "OR" options (e.g., (a) OR (b)), treat each option as a separate question with its own entry in the output.
        #    - Remove any "(a)" or "(b)" prefixes from the question text to ensure a clean format (e.g., "How did the Silk Route connect the world ?" instead of "(a) How did the Silk Route connect the world ?").
        #    - For Section E, include the entire source passage and all sub-questions as one question. Format sub-questions with "a)", "b)", "c)" prefixes (e.g., "a) At what interval is census conducted in India ?") instead of numerical labels (e.g., "35.1").
        #    - For Section F, include the entire question with all parts (e.g., 37(a) and 37(b)) as one question.
        # 2. **Marks**: 
        #    - Provide the total marks as a single number (e.g., "5" instead of "2+3=5") based on the section's mark scheme.
        #    - For Section A, each MCQ has 1 mark.
        #    - For Section B, each question (including OR options) has 2 marks.
        #    - For Section C, each question (including OR options) has 3 marks.
        #    - For Section D, each question (including OR options) has 5 marks.
        #    - For Section E, each question (34, 35, 36) has a total of 4 marks.
        #    - For Section F, question 37 has a total of 5 marks.
        # 3. **Image Association**: 
        #    - Include "imgUrl": "1" if the question mentions "picture", "figure", "diagram", or similar terms indicating a visual element (except for map-based questions).
        #    - For Section F (map-based), always include "imgUrl": "2".
        # 4. **Exclusions**: 
        #    - Ignore instructions, notes, or alternative questions for visually impaired candidates.
        #    - Ignore text in languages other than English.

        # Return the result in this JSON format:
        # [
        #     {"question": "...", "marks": "..."},
        #     {"question": "...", "marks": "...", "imgUrl": "1"},
        #     {"question": "...", "marks": "...", "imgUrl": "2"}
        # ]
        # Ensure all numbered questions (1 to 37, including separate OR options) are extracted with consistent formatting, accurate marks, and no duplicate entries. For Section A, ensure exactly 20 MCQs are extracted, each with its full question text and options.
        # """
        #7
        # base_prompt = """
        # Extract all the questions from the following question paper pdf, adhering to its sectional structure: 
        # - Section A: Questions 1 to 20 are Multiple Choice Questions (MCQs), each worth 1 mark.
        # - Section B: Questions 21 to 24 are Very Short Answer questions, each worth 2 marks.
        # - Section C: Questions 25 to 29 are Short Answer questions, each worth 3 marks.
        # - Section D: Questions 30 to 33 are Long Answer questions, each worth 5 marks.
        # - Section E: Questions 34 to 36 are Case-based/Source-based questions, each with sub-questions, totaling 4 marks per question.
        # - Section F: Question 37 is a Map skill-based question with parts, totaling 5 marks.

        # For each question, follow these rules:
        # 1. **Question Text**: 
        #    - For Section A (MCQs, questions 1 to 20), include the full question text with the stem and all options (e.g., (A), (B), (C), (D)) in a single entry. Do not extract incomplete MCQs (e.g., question stem without options) or create duplicate entries.
        #    - For questions with "OR" options (e.g., (a) OR (b)), treat each option as a separate question with its own entry in the output.
        #    - Remove any "(a)" or "(b)" prefixes from the question text to ensure a clean format (e.g., "How did the Silk Route connect the world ?" instead of "(a) How did the Silk Route connect the world ?").
        #    - For Section E, include the entire source passage and all sub-questions as one question. Format sub-questions with "a)", "b)", "c)" prefixes (e.g., "a) At what interval is census conducted in India ?") instead of numerical labels (e.g., "35.1").
        #    - For Section F, include the entire question with all parts (e.g., 37(a) and 37(b)) as one question.
        # 2. **Marks**: 
        #    - Provide the total marks as a single number (e.g., "5" instead of "2+3=5") based on the section's mark scheme.
        #    - For Section A, each MCQ has 1 mark.
        #    - For Section B, each question (including OR options) has 2 marks.
        #    - For Section C, each question (including OR options) has 3 marks.
        #    - For Section D, each question (including OR options) has 5 marks.
        #    - For Section E, each question (34, 35, 36) has a total of 4 marks.
        #    - For Section F, question 37 has a total of 5 marks.
        # 3. **Image Association**: 
        #    - Include "imgUrl": "1" if the question mentions "picture", "figure", "diagram", or similar terms indicating a visual element (except for map-based questions).
        #    - For Section F (map-based), always include "imgUrl": "2".
        # 4. **Exclusions**: 
        #    - Ignore instructions, notes, or alternative questions for visually impaired candidates.
        #    - Ignore text in languages other than English.

        # Return the result in this JSON format:
        # [
        #     {"question": "...", "marks": "..."},
        #     {"question": "...", "marks": "...", "imgUrl": "1"},
        #     {"question": "...", "marks": "...", "imgUrl": "2"}
        # ]
        # Ensure all numbered questions (1 to 37, including separate OR options) are extracted with consistent formatting, accurate marks, and no duplicate entries. For Section A, ensure exactly 20 MCQs are extracted, each with its full question text and options.
        # """
        #8
        base_prompt = """
        Extract all questions from the provided PDF question paper, adhering to its sectional structure:
        - Section A: Questions 1 to 20 are Multiple Choice Questions (MCQs), each worth 1 mark.
        - Section B: Questions 21 to 24 are Very Short Answer questions, each worth 2 marks.
        - Section C: Questions 25 to 29 are Short Answer questions, each worth 3 marks.
        - Section D: Questions 30 to 33 are Long Answer questions, each worth 5 marks.
        - Section E: Questions 34 to 36 are Case-based/Source-based questions, each with three sub-questions, totaling 4 marks per question.
        - Section F: Question 37 is a Map skill-based question with parts, totaling 5 marks.

        For each question, follow these rules:
        1. **Question Text**:
           - For Section A (MCQs, questions 1 to 20):
             * ALWAYS keep the question stem and its options together as a single question entry
             * NEVER split an MCQ into separate entries for the stem and options
             * Format MCQs as: "Question stem\n(A) Option A\n(B) Option B\n(C) Option C\n(D) Option D"
             * If an MCQ spans multiple lines, combine them into a single coherent question
           - For questions with "OR" options (e.g., 24(a) OR 24(b)), treat each option as a separate question with its own entry, removing "(a)" or "(b)" prefixes from the question text.
           - For Section E, include the entire source passage and all sub-questions as one question. Format sub-questions with "a)", "b)", "c)" prefixes (e.g., "a) At what interval is census conducted in India?") instead of numerical labels (e.g., "34.1").
           - For Section F, include the entire question with all parts (e.g., 37(a) and 37(b)) as one question.
           - Ensure the question text is complete, including any introductory statements or instructions (e.g., "Analyse the statement," "Explain with examples").
        2. **Marks**:
           - Assign marks based on the section's mark scheme: Section A (1 mark), Section B (2 marks), Section C (3 marks), Section D (5 marks), Section E (4 marks), Section F (5 marks).
           - For OR questions, assign the same marks to each option as the original question.
        3. **Image Association**:
           - Include "imgUrl": "1" only if the question explicitly mentions "picture," "figure," "diagram," or similar terms (e.g., question 17: "Study the given picture").
           - For Section F (map-based, question 37), always include "imgUrl": "2".
           - Do not assign "imgUrl" unless explicitly indicated in the question text.
        4. **Exclusions**:
           - Ignore instructions, notes, or alternative questions for visually impaired candidates (e.g., question 17 and 37 alternatives).
           - Ignore text in languages other than English (e.g., Hindi instructions).
           - Exclude incomplete or ambiguous fragments (e.g., "s.", "Illustrate with examples.") unless they are part of a valid question.
        5. **Formatting**:
           - Remove extraneous characters (e.g., leading commas, stray punctuation) from the question text.
           - Ensure consistent formatting, with no truncated or partial questions.
           - For MCQs, ensure the question stem and all options are properly formatted and combined into a single entry.

        Return the result in this JSON format:
        [
            {"question": "...", "marks": "..."},
            {"question": "...", "marks": "...", "imgUrl": "1"},
            {"question": "...", "marks": "...", "imgUrl": "2"}
        ]
        Ensure all 37 numbered questions (including separate OR options) are extracted with complete text, accurate marks, and no duplicates. For Section A, extract exactly 20 MCQs, each with its full stem and options. For Section E, group sub-questions under one entry per question.
        """
        
        prompt = f"{custom_prompt}\n\n{text}" if custom_prompt else f"{base_prompt}\n\n{text}"

        # Step 3: Use the Gemini model
        # response = model.generate_content(prompt)
        response = model.generate_content([
            prompt,
            {"mime_type": "application/pdf", "data": content}
        ])
        extracted_data = response.text.strip()

        # Optional: Clean up markdown-style code block
        if extracted_data.startswith("```json"):
            extracted_data = extracted_data[7:-3].strip()

        parsed_data = json.loads(extracted_data)

        # Step 4: Return structured JSON
        return JSONResponse(content={
            "status": "success",
            "data": parsed_data
        })

    except json.JSONDecodeError as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"JSON parse error: {str(e)}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


# First, let's create the request model
class QuestionItem(BaseModel):
    question: str
    marks: str
    imgUrl: str = None  # Optional field

class QuestionListRequest(BaseModel):
    data: List[QuestionItem]
    src: str
    is_pyq: bool
    when_pyq: str = None  # Optional field

@app.post("/store-questions")
async def store_questions(payload: QuestionListRequest):
    try:
        # Will store all the rows to be inserted
        questions_to_insert = []
        
        # Process each question
        for question_item in payload.data:
            # Step 1: Get question embedding
            question_embedding = gemini_func.compute_embeddings([question_item.question])[0]
            
            # Step 2: Find matching subtopic using vector search
            response = supabase.rpc("match_question_vector", {
                "input_embedding": question_embedding
            }).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail=f"No matching subtopic found for question: {question_item.question[:50]}...")
            
            # Get the best matching subtopic (first result has highest similarity)
            best_match = response.data[0]

            
            # Step 3: Prepare row for insertion
            question_row = {
                "question": question_item.question,
                "expanded_syllabus_id": best_match["id"],  # ID of the best matching subtopic
                "difficulty": "Medium",  # Default value, can be modified based on requirements
                "is_pyq": payload.is_pyq,  # Assuming these are PYQs, can be modified based on requirements
                "when_pyq": payload.when_pyq,  # Can be modified based on requirements
                "src": payload.src,  # Can be modified based on requirements
                "embedding": question_embedding,
                "marks": question_item.marks
            }
            
            # Add imgUrl if present
            if question_item.imgUrl:
                question_row["imgurl"] = question_item.imgUrl
                
            questions_to_insert.append(question_row)
        
        # Step 4: Bulk insert into question_set table
        response = supabase.table("question_set").insert(questions_to_insert).execute()
        
        return {
            "status": "success",
            "inserted_count": len(questions_to_insert),
            "message": f"Questions successfully stored in question_set for {payload.src}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing questions: {str(e)}")



class ChaptersSubtopicsRequest(BaseModel):
    class_name: str
    subject: str

@app.post("/get-chapters-subtopics")
async def get_chapters_subtopics(payload: ChaptersSubtopicsRequest):
    try:
        # Call the Supabase RPC function
        response = supabase.rpc("get_chapters_subtopics", {
            "input_class": payload.class_name,
            "input_subject": payload.subject
        }).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="No chapters or subtopics found for the given class and subject.")

        # Return the JSON response directly
        return {
            "status": "success",
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")




class RandomQuestionRequest(BaseModel):
    subtopic_id: str
    marks: str
    is_pyq: bool = True

@app.get("/get-random-question")
async def get_random_question(payload: RandomQuestionRequest):
    try:
        # Call the Supabase RPC function
        response = supabase.rpc("get_random_question", {
            "input_subtopic_id": payload.subtopic_id,  # Convert UUID to string
            "input_marks": payload.marks,
            "input_is_pyq": payload.is_pyq
        }).execute()

       # Check if a question was found
        if not response.data:
            raise HTTPException(status_code=404, detail="No question found for the specified subtopic_id, marks, and is_pyq status.")

        # Return the JSON response
        return {
            "status": "success",
            "data": response.data
        }

    except HTTPException:
        # Re-raise HTTPException to preserve the intended status code (e.g., 404)
        raise

    except Exception as e:
        # Handle other unexpected errors with a 500 status code
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



# class SectionRequest(BaseModel):
#     question_count: int
#     marks_per_question: str

# class QuestionPaperRequest(BaseModel):
#     sections: List[SectionRequest]

class SectionRequest(BaseModel):
    question_count: int
    marks_per_question: str
    metadata: Optional[List[str]] = None

class QuestionPaperRequest(BaseModel):
    equal_distribution: bool
    sections: List[SectionRequest]


@app.post("/generate-question-paper")
async def generate_question_paper(payload: QuestionPaperRequest):

    try:
        # Initialize response structure
        result = {
            "status": "success",
            "question_paper": []
        }

        # Generate section names (Section A, Section B, etc.)
        section_names = [f"Section {chr(65 + i)}" for i in range(len(payload.sections))]

        # Process each section
        for idx, section in enumerate(payload.sections):
            # Call the Supabase RPC function to get random questions
            response = supabase.rpc("get_random_questions_by_marks", {
                "input_marks": section.marks_per_question,
                "input_count": section.question_count
            }).execute()

            # Get questions from response
            questions = response.data or []
            print(f"Section {section_names[idx]}: Requested {section.question_count} questions with marks {section.marks_per_question}, Got {len(questions)}")

            # Validate the number of questions returned
            if len(questions) != section.question_count:
                raise HTTPException(
                    status_code=500,
                    detail=f"Expected {section.question_count} questions for marks {section.marks_per_question} in section {section_names[idx]}, but got {len(questions)}"
                )

            # Add section to result, including number_of_questions
            result["question_paper"].append({
                "section_name": section_names[idx],
                "marks_per_question": section.marks_per_question,
                "number_of_questions": str(len(questions)),  # Convert to string to match example
                "questions": questions
            })

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



# class SectionRequest(BaseModel):
#     question_count: int
#     marks_per_question: str
#     metadata: Optional[List[str]] = None

# class QuestionPaperRequest(BaseModel):
#     equal_distribution: bool
#     sections: List[SectionRequest]

# @app.post("/generate-question-paper-v2")
# async def generate_question_paper_v2(payload: QuestionPaperRequest):
#     try:
#         # Initialize response structure
#         result = {
#             "status": "success",
#             "question_paper": []
#         }

#         # Generate section names (Section A, Section B, etc.)
#         section_names = [f"Section {chr(65 + i)}" for i in range(len(payload.sections))]

#         # Define all possible subparts for equal distribution
#         all_subparts = ["history", "geography", "political science", "economics"]

#         # Process each section
#         for idx, section in enumerate(payload.sections):
#             section_questions = []

#             if payload.equal_distribution:
#                 # Determine subparts to distribute across
#                 subparts = section.metadata if section.metadata else all_subparts
#                 if not subparts:
#                     raise HTTPException(status_code=400, detail=f"No subparts specified for equal distribution in section {section_names[idx]}")

#                 # Calculate questions per subpart
#                 questions_per_subpart = section.question_count // len(subparts)
#                 remainder = section.question_count % len(subparts)

#                 # Fetch questions for each subpart
#                 for subpart_idx, subpart in enumerate(subparts):
#                     count = questions_per_subpart + (1 if subpart_idx < remainder else 0)
#                     if count == 0:
#                         continue

#                     # Call RPC to get questions for this subpart
#                     response = supabase.rpc("get_random_questions_by_marks_and_metadata", {
#                         "input_marks": section.marks_per_question,
#                         "input_metadata": subpart,
#                         "input_count": count
#                     }).execute()

#                     questions = response.data or []
#                     print(f"Section {section_names[idx]}, Subpart {subpart}: Requested {count} questions with marks {section.marks_per_question}, Got {len(questions)}")

#                     # Validate number of questions
#                     if len(questions) < count:
#                         raise HTTPException(
#                             status_code=500,
#                             detail=f"Insufficient questions for subpart {subpart} in section {section_names[idx]}: Requested {count}, Got {len(questions)}"
#                         )

#                     section_questions.extend(questions)

#             else:
#                 # Non-equal distribution
#                 if section.metadata:
#                     # Fetch questions for specified subparts
#                     for subpart in section.metadata:
#                         response = supabase.rpc("get_random_questions_by_marks_and_metadata", {
#                             "input_marks": section.marks_per_question,
#                             "input_metadata": subpart,
#                             "input_count": section.question_count // len(section.metadata)
#                         }).execute()

#                         questions = response.data or []
#                         print(f"Section {section_names[idx]}, Subpart {subpart}: Requested {section.question_count // len(section.metadata)} questions with marks {section.marks_per_question}, Got {len(questions)}")

#                         if len(questions) < section.question_count // len(section.metadata):
#                             raise HTTPException(
#                                 status_code=500,
#                                 detail=f"Insufficient questions for subpart {subpart} in section {section_names[idx]}: Requested {section.question_count // len(section.metadata)}, Got {len(questions)}"
#                             )

#                         section_questions.extend(questions)
#                 else:
#                     # Use original RPC for no metadata filtering
#                     response = supabase.rpc("get_random_questions_by_marks", {
#                         "input_marks": section.marks_per_question,
#                         "input_count": section.question_count
#                     }).execute()

#                     questions = response.data or []
#                     print(f"Section {section_names[idx]}: Requested {section.question_count} questions with marks {section.marks_per_question}, Got {len(questions)}")

#                     if len(questions) < section.question_count:
#                         raise HTTPException(
#                             status_code=500,
#                             detail=f"Insufficient questions for section {section_names[idx]}: Requested {section.question_count}, Got {len(questions)}"
#                         )

#                     section_questions = questions

#             # Add section to result
#             result["question_paper"].append({
#                 "section_name": section_names[idx],
#                 "marks_per_question": section.marks_per_question,
#                 "number_of_questions": str(len(section_questions)),
#                 "questions": section_questions
#             })

#         return result

#     except HTTPException:
#         raise

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class SubpartRequirement(BaseModel):
    metadata: str
    question_count: int
    marks_per_question: str

class SectionRequest(BaseModel):
    question_count: Optional[int] = None
    marks_per_question: Optional[str] = None
    metadata: Optional[List[str]] = None
    subpart_requirements: Optional[List[SubpartRequirement]] = None

class QuestionPaperRequest(BaseModel):
    equal_distribution: bool
    sections: List[SectionRequest]

# FastAPI Route
@app.post("/generate-question-paper-v2")
async def generate_question_paper_v2(payload: QuestionPaperRequest):
    try:
        result = {
            "status": "success",
            "question_paper": []
        }
        section_names = [f"Section {chr(65 + i)}" for i in range(len(payload.sections))]
        all_subparts = ["history", "geography", "political science", "economics"]

        for idx, section in enumerate(payload.sections):
            section_questions = []

            if payload.equal_distribution:
                # Equal distribution logic
                if section.subpart_requirements:
                    raise HTTPException(status_code=400, detail=f"subpart_requirements should not be provided when equal_distribution is true for section {section_names[idx]}")

                subparts = section.metadata if section.metadata else all_subparts
                if not subparts:
                    raise HTTPException(status_code=400, detail=f"No subparts specified for equal distribution in section {section_names[idx]}")

                if not section.question_count or not section.marks_per_question:
                    raise HTTPException(status_code=400, detail=f"question_count and marks_per_question are required when equal_distribution is true for section {section_names[idx]}")

                questions_per_subpart = section.question_count // len(subparts)
                remainder = section.question_count % len(subparts)

                for subpart_idx, subpart in enumerate(subparts):
                    count = questions_per_subpart + (1 if subpart_idx < remainder else 0)
                    if count == 0:
                        continue

                    response = supabase.rpc("get_random_questions_by_marks_and_metadata", {
                        "input_marks": section.marks_per_question,
                        "input_metadata": subpart,
                        "input_count": count
                    }).execute()

                    questions = response.data or []
                    if len(questions) < count:
                        raise HTTPException(status_code=500, detail=f"Insufficient questions for subpart {subpart} in section {section_names[idx]}: Requested {count}, Got {len(questions)}")

                    section_questions.extend(questions)

            else:
                # Non-equal distribution with specified subpart_requirements
                if not section.subpart_requirements:
                    # If no subpart_requirements, assume metadata and question_count are provided
                    if not section.metadata or not section.question_count:
                        raise HTTPException(status_code=400, detail=f"metadata and question_count must be provided when equal_distribution is false and subpart_requirements is not specified for section {section_names[idx]}")

                    # Convert metadata and total question_count into subpart_requirements
                    total_questions = section.question_count
                    subparts = section.metadata
                    default_marks = section.marks_per_question or "1"
                    questions_per_subpart = total_questions // len(subparts)
                    remainder = total_questions % len(subparts)
                    subpart_reqs = [
                        SubpartRequirement(
                            metadata=subpart,
                            question_count=questions_per_subpart + (1 if i < remainder else 0),
                            marks_per_question=default_marks
                        )
                        for i, subpart in enumerate(subparts)
                    ]
                else:
                    subpart_reqs = section.subpart_requirements
                    total_questions = sum(req.question_count for req in subpart_reqs)
                    if section.question_count and section.question_count != total_questions:
                        raise HTTPException(status_code=400, detail=f"Total question_count ({section.question_count}) does not match sum of subpart_requirements ({total_questions}) for section {section_names[idx]}")

                # Fetch questions based on subpart_requirements
                for requirement in subpart_reqs:
                    response = supabase.rpc("get_random_questions_by_marks_and_metadata", {
                        "input_marks": requirement.marks_per_question,
                        "input_metadata": requirement.metadata,
                        "input_count": requirement.question_count
                    }).execute()

                    questions = response.data or []
                    if len(questions) < requirement.question_count:
                        raise HTTPException(status_code=500, detail=f"Insufficient questions for subpart {requirement.metadata} with marks {requirement.marks_per_question} in section {section_names[idx]}: Requested {requirement.question_count}, Got {len(questions)}")

                    section_questions.extend(questions)

            result["question_paper"].append({
                "section_name": section_names[idx],
                "questions": section_questions
            })

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")