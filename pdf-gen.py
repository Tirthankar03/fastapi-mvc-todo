from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import json
import re

def generate_question_paper_pdf(json_data, output_filename="question_paper.pdf"):
    # Initialize PDF
    doc = SimpleDocTemplate(output_filename, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=12,
        alignment=1  # Center
    )
    
    section_style = ParagraphStyle(
        name='Section',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6
    )
    
    question_style = ParagraphStyle(
        name='Question',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        spaceAfter=6
    )
    
    # Content list for PDF
    content = []
    
    # Title
    content.append(Paragraph("Social Science Question Paper", title_style))
    content.append(Spacer(1, 0.2 * inch))
    
    # Instructions
    instructions = """
    <b>General Instructions:</b><br/>
    1. The question paper is divided into six sections: A, B, C, D, E, and F.<br/>
    2. Section A: Questions 1 to 20 are Multiple Choice Questions (MCQs), each carrying 1 mark.<br/>
    3. Section B: Questions 21 to 24 are Very Short Answer questions, each carrying 2 marks.<br/>
    4. Section C: Questions 25 to 29 are Short Answer questions, each carrying 3 marks.<br/>
    5. Section D: Questions 30 to 33 are Long Answer questions, each carrying 5 marks.<br/>
    6. Section E: Questions 34 to 36 are Case-based/Source-based questions, each carrying 4 marks (with three sub-questions).<br/>
    7. Section F: Question 37 is a Map skill-based question, carrying 5 marks (with parts).<br/>
    8. All questions are compulsory.<br/>
    9. For questions with images, refer to the attached figures.<br/>
    10. Read the questions carefully before answering.
    """
    content.append(Paragraph(instructions, question_style))
    content.append(Spacer(1, 0.2 * inch))
    
    # Parse JSON
    question_paper = json_data.get("question_paper", [])
    question_number = 1
    
    for section in question_paper:
        section_name = section.get("section_name", "Unknown Section")
        questions = section.get("questions", [])
        
        # Section Header
        content.append(Paragraph(section_name, section_style))
        
        # Section-specific instructions
        if section_name == "Section E":
            content.append(Paragraph("<i>Each question in this section has three sub-questions.</i>", question_style))
        elif section_name == "Section F":
            content.append(Paragraph("<i>Attach the provided map for Question 37. Answer all parts.</i>", question_style))
        
        # Questions
        for question in questions:
            question_text = question.get("question", "No question text")
            marks = question.get("marks", "Unknown")
            img_url = question.get("imgUrl")
            
            # Replace \n with <br/> for line breaks
            question_text = re.sub(r'\\n', '<br/>', question_text)
            
            # Add image placeholder if imgUrl exists
            if img_url:
                question_text += "<br/><i>[Refer to Image]</i>"
            
            # Format question with number and marks
            question_line = f"{question_number}. {question_text} ({marks} mark{'s' if int(marks) > 1 else ''})"
            content.append(Paragraph(question_line, question_style))
            
            # Optionally embed image (uncomment if images are accessible)
            # if img_url:
            #     try:
            #         content.append(Image(img_url, width=2*inch, height=2*inch))
            #     except Exception as e:
            #         content.append(Paragraph(f"<i>[Image not available: {str(e)}]</i>", question_style))
            
            question_number += 1
        
        content.append(Spacer(1, 0.1 * inch))
    
    # Build PDF
    doc.build(content)
    print(f"PDF generated: {output_filename}")

# Example usage
if __name__ == "__main__":
    # Sample JSON data with \n and imgUrl
    sample_json = {
    "status": "success",
    "question_paper": [
        {
            "section_name": "Section A",
            "questions": [
                {
                    "id": "de592d04-4a04-41a9-a52b-2a92269ee8ec",
                    "question": "Arrange the following in chronological order and choose the correct option :\nI. The Bretton Woods conference established the International Monetary Fund.\nII. The Second World War broke out between the Axis and Allied groups.\nIII. A car manufacturer Henry Ford adopted the 'Assembly Line Method' for production.\nIV. The Western economies organized themselves as a group 'The Group of 77'.\nOptions:\n(A) III, II, I and IV\n(B) I, II, III and IV\n(C) IV, III, II and I\n(D) IV, II, III and I",
                    "expanded_syllabus_id": "12b1747d-bbe1-4f84-88cc-eddfae5a0a20",
                    "subtopic": "Post-war settlement and the Bretton Woods Institutions",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 32-1-1 Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "47439f34-e960-4cce-9c46-edc9ea6fe5c7",
                    "question": "Which one of the following aspects was common between the writings of B.R. Ambedkar and E.V. Ramaswamy Naicker ?\n(A) Wrote on the caste system in India\n(B) Highlighted the experiences of women\n(C) Raised awareness about cultural heritage\n(D) Motivated Indians for their national freedom.",
                    "expanded_syllabus_id": "44bf0a62-55d5-4d81-9428-1d0d3d43ca4f",
                    "subtopic": "The movement to revive Indian folklore",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 32-1-1 Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "472a8efe-be40-48ea-aae0-67ba2a444f18",
                    "question": "‘Buddhism emerged from eastern India and spread in several directions.’\nRead the following reasons for its spread and choose the correct option.\nI. Due to Cultural exchange\nII. Due to Silk route\nIII. Due to trade & travellers\nIV. Due to European efforts\nOptions:\n(A) Only I, II and IV are correct.\n(B) Only II, III and IV are correct.\n(C) Only I, II and III are correct.\n(D) Only I, III and IV are correct.",
                    "expanded_syllabus_id": "9415f0bb-61f3-4c7d-871c-b151a9b7ce77",
                    "subtopic": "The silk routes and cultural exchange",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-3-3 Set 3",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "13d90981-31c2-42c9-b81b-428c4c9a14fd",
                    "question": "Arrange the following events in chronological order and choose the correct option. I. Treaty of Constantinople II. Hamburg granted autonomy to Hungary III. Balkan Conflict IV. Napoleonic Civil Code Options: (A) IV, II, I & III (B) III, II, IV & I (C) IV, I, II & III (D) I, IV, III & II",
                    "expanded_syllabus_id": "23f2c9cb-421d-4608-8fcf-1c85b4521f91",
                    "subtopic": "The Civil Code of 1804",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-2-2 Set 2",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "e40608cb-1274-459b-bee8-869e3ce993c2",
                    "question": "Two statements are given below. They are Assertion (A) and Reason (R). Read both the statements and choose the correct option. Assertion (A) : ‘The Act of Union 1707’ between England and Scotland resulted in the formation of ‘United Kingdom of Great Britain’. Reason (R): England wanted to impose its influence on Scotland. Options: (A) Both (A) and (R) are true and (R) is the correct explaination of (A). (B) Both (A) and (R) are true but (R) is not the correct explaination of (A). (C) (A) is true but (R) is false. (D) (A) is false but (R) is true.",
                    "expanded_syllabus_id": "f905b647-b0f7-4f5c-8cac-417ede144b51",
                    "subtopic": "The Making of a 'British Nation'",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-2-2 Set 2",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "bbfdae69-9984-4c46-b368-3393f4a62d44",
                    "question": "Who of the following set up the first Iron and Steel industry in India?\n(A) J.R.D. Tata\n(B) Purushotam Das\n(C) R.G. Saraiya\n(D) Thakur Das",
                    "expanded_syllabus_id": "1a215bc8-8b2a-44a0-b158-3b57b42e3ab0",
                    "subtopic": "Iron and Steel Industry",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 32-1-1 Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "e9bd5969-e34c-4e67-9d97-636ff935ddae",
                    "question": "Read the following informations and identify the crop.\nIt is the staple food crop of majority of people in India.\nIndia is the second largest producer of this crop.\nIt is a Kharif crop.\nIt requires high humidity with 100 cm of annual rainfall.\nCrops:\n(A) Ragi\n(B) Bajra\n(C) Wheat\n(D) Rice",
                    "expanded_syllabus_id": "889bd624-66cd-44f8-9161-42196011f9b3",
                    "subtopic": "Major Crops: Rice",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-3-3 Set 3",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "18a75ef9-6318-4ab2-a1e2-b3c27c691305",
                    "question": "Identify the crop with the help of the given information.\n India is the largest producer as well as the consumer of this crop.\n This crop provides the major source of protein in a vegetarian diet.\n This crop needs less moisture and survives even in dry conditions.\n This crop is mostly grown in rotation with other crops.\nOptions :\n(a) Wheat\n(b) Bajra\n(c) Pulses\n(d) Rice",
                    "expanded_syllabus_id": "d35a5f49-6717-4cea-b1e1-65a76b3ef966",
                    "subtopic": "Major Crops: Pulses",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 contemporary Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "ab82691f-d0d4-48cd-8c2e-b6788acf5015",
                    "question": "Identify the soil with the help of following information.\n• It develops in areas with high temperature.\n• It is the result of intense leaching due to heavy rain.\n• Humus content is low.\nSoil:\n(a) Arid soil\n(b) Yellow soil\n(c) Laterite soil\n(d) Black soil",
                    "expanded_syllabus_id": "8039d08e-d5a0-48c4-81c0-3d339908c43d",
                    "subtopic": "Classification of different soils (Laterite Soil)",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-1-1 Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "466645a6-90c9-4829-9100-0d6b8badae3b",
                    "question": "Which one of the following is the irrigation system in Meghalaya?\n(A) To irrigate land only during rainy season.\n(B) To use large volumes of water for irrigation.\n(C) To remove water from soil.\n(D) To use bamboo drip irrigation system.",
                    "expanded_syllabus_id": "56f8c0d3-3d80-4dcc-83d0-83f621529329",
                    "subtopic": "Bamboo drip irrigation system",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-3-3 Set 3",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "b54f67a7-9c37-4e3b-abaf-27605fca57b7",
                    "question": "Identify the primary objective of power sharing arrangements in Belgium from the following options.\n(A) Establishing a unitary form of government.\n(B) Centralized political control of government.\n(C) Establishing cultural and educational matters of Dutch.\n(D) Accommodating linguistic and regional interest.",
                    "expanded_syllabus_id": "edc5e726-f683-4dfe-9063-dd9ad36ead8a",
                    "subtopic": "Elements of the Belgian model of accommodation",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-3-3 Set 3",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "political science"
                },
                {
                    "id": "e9b86914-cca0-433d-a996-353bd187e206",
                    "question": "How do Political Parties ensure accountability to the public? Choose the most suitable option from the following.\n(A) Through Press Conferences\n(B) Through Social Media Campaigns\n(C) Through encouraging Partisanship\n(D) Through Elections and Voter Support",
                    "expanded_syllabus_id": "7d2966ee-2f1a-417a-8a98-6efebda1b679",
                    "subtopic": "Need for political parties",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-3-3 Set 3",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "political science"
                },
                {
                    "id": "5b3220d8-b059-4d0e-bef7-2f28929bef4b",
                    "question": "In which one of the following regions is the participation of women in public life the highest ?\n(a) Nordic countries\n(b) Arab states\n(c) European countries\n(d) Asian countries",
                    "expanded_syllabus_id": "b839abcd-91eb-45c3-9bdc-5bac95fdfbe5",
                    "subtopic": "Women's minimal role in public life and politics",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 32-2-1 Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "political science"
                },
                {
                    "id": "594ca211-d778-41fb-8b90-bec51d809787",
                    "question": "Choose the correct option regarding the Concurrent List of legislative rights in \nIndia.\n(A) Currency, Irrigation, Adoption and Computer Software\n(B) Defense, Foreign Affairs, Banking and Communication\n(C) Police, Business, Commerce and Agriculture\n(D) Education, Forest, Marriage and Adoption",
                    "expanded_syllabus_id": "24942e1e-ceac-48bb-807c-d3c202cee11d",
                    "subtopic": "Three-Fold Distribution of Legislative Powers in India: Union List, State List, Concurrent List",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 contemporary Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "political science"
                },
                {
                    "id": "849288b4-d3fd-4403-94fa-e41277e1368a",
                    "question": "Two statements are given below as Assertion (A) and Reason (R). Read the Statements and choose the correct option :\nAssertion (A) : Elections are the spirit of democracy.\nReason (R): Elections expand Political participation.\nOptions:\n(A) Both (A) and (R) are true and (R) is the correct explanation of (A).\n(B) Both (A) and (R) are true, but (R) is the not correct explanation of (A).\n(C) (A) is true, but (R) is false.\n(D) (A) is false, but (R) is true.",
                    "expanded_syllabus_id": "dc5af3c4-aa8a-476d-a8c7-76d2aacdaa17",
                    "subtopic": "Encouraging participation in political parties",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 32-1-1 Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "political science"
                },
                {
                    "id": "60f81cc6-9662-49c0-8c50-9b9481a14db9",
                    "question": "Assume there are four families in a locality. If the incomes of these four families in a week are ` 2,000, ` 5,000, ` 3,000 and ` 6,000, then the weekly average income of the locality will be – (A) ` 4,000 (B) ` 5,000 (C) ` 2,000 (D) ` 1,000",
                    "expanded_syllabus_id": "9e962d79-fd1a-4373-a7bd-4496ea5efbae",
                    "subtopic": "Comparison of Per Capita Income of Select States",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-2-2 Set 2",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "economics"
                },
                {
                    "id": "f8385465-621e-4e6f-a6d2-0e6be38782ba",
                    "question": "Two statements are given below. They are Assertion (A) and Reason (R).\nRead both the statements and choose the correct option.\nAssertion (A) :\nBanks are not ready to lend money to certain borrowers.\nReason (R) :\nSome people do not have collateral.\nOptions :\n(A) Both (A) and (R) are true and (R) is the correct explanation of (A).\n(B) Both (A) and (R) are true, but (R) is not the correct explanation of (A).\n(C) (A) is true, but (R) is false.\n(D) (A) is false, but (R) is true.",
                    "expanded_syllabus_id": "983988ed-2cfe-4dcb-b2d3-6e5f7f3ed8e3",
                    "subtopic": "Importance of Affordable Credit",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-4-2 Set 2",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "economics"
                },
                {
                    "id": "8e590b21-9698-4e05-8c73-4ed184bcfe08",
                    "question": "Choose the correct option to fill the blank.\nRemoving barriers or restrictions on business and trade set by the government is called as ________.\n(a) Disinvestment\n(b) Special Economic Zones\n(c) Liberalisation\n(d) Foreign Direct Investment",
                    "expanded_syllabus_id": "c2b0ef3c-5f45-4799-a3e4-6a272a57ccf3",
                    "subtopic": "Liberalization by removing barriers",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-1-1 Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "economics"
                },
                {
                    "id": "3ac36d61-1810-4120-8df0-08b7a4a9e78a",
                    "question": "Which one of the following organization is providing data regarding employment in India?\n(A) National Statistical Office\n(B) Niti Ayog\n(C) National Informatics Centre\n(D) Public Service Commission",
                    "expanded_syllabus_id": "52b1a010-35a7-4503-aab5-1b2d085e3724",
                    "subtopic": "Employment distribution across sectors",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 32-1-1 Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "economics"
                },
                {
                    "id": "fd30868d-d20d-4bc5-98e5-a40ca6c7dec3",
                    "question": "Kamalkant is a shopkeeper who pays his taxes on time, however none of the workers in his shop get any paid leave in the year. On the basis of the given situation, find out the correct option.\n(a) Workers are employed in the organised sector.\n(b) Workers are engaged in the unorganised sector.\n(c) Workers are employed in the joint sector.\n(d) Workers are employed in the public sector.",
                    "expanded_syllabus_id": "36a052a4-031a-4cfe-b47d-f38f8d986f2d",
                    "subtopic": "Organised and Unorganised sectors",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 contemporary Set 1",
                    "marks": "1",
                    "imgUrl": null,
                    "metadata": "economics"
                }
            ]
        },
        {
            "section_name": "Section B",
            "questions": [
                {
                    "id": "b98ca323-a51e-4402-b07b-8710454a5802",
                    "question": "\"The Silk route was a good example of vibrant pre-modern trade and cultural links between distant parts of the world.\" Explain the statement with any two examples.",
                    "expanded_syllabus_id": "9415f0bb-61f3-4c7d-871c-b151a9b7ce77",
                    "subtopic": "The silk routes and cultural exchange",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-1-1 Set 1",
                    "marks": "2",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "21dd8323-b1c4-4072-b29f-8f714d70cb53",
                    "question": "Explain any two technological reforms initiated by the Indian Government in agriculture.",
                    "expanded_syllabus_id": "7e3160af-2cd3-4ce9-9a5f-26fe57217515",
                    "subtopic": "Technological and Institutional Reforms in Agriculture",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 contemporary Set 1",
                    "marks": "2",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "d2ac9e92-e75b-4dad-ac19-fd8be571d556",
                    "question": "Examine the role of the Supreme Court in the Federal System of India in two points.",
                    "expanded_syllabus_id": "67ac6677-ce98-480d-8553-8b12fa38b566",
                    "subtopic": "Role of the Judiciary in Federalism",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-4-2 Set 2",
                    "marks": "2",
                    "imgUrl": null,
                    "metadata": "political science"
                },
                {
                    "id": "7b00c7e7-8c41-49fa-8fcf-713a765d4267",
                    "question": "Differentiate between Public and Private Sector.",
                    "expanded_syllabus_id": "6215c491-f9a8-4685-b4cb-7c49fb5dcba5",
                    "subtopic": "Public and Private sectors",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-1-1 Set 1",
                    "marks": "2",
                    "imgUrl": null,
                    "metadata": "economics"
                }
            ]
        },
        {
            "section_name": "Section C",
            "questions": [
                {
                    "id": "3a81b1a0-2a51-4d18-a8c6-ac2d5b20cb4b",
                    "question": "In India, the growth of modern nationalism was intimately connected to \nthe anti-colonial movement\nAnalyse the statement.",
                    "expanded_syllabus_id": "97c619e5-4490-432a-bc19-910c45e21749",
                    "subtopic": "The connection between nationalism and the anti-colonial movement",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 contemporary Set 1",
                    "marks": "3",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "9a7b4241-e6bc-4230-afc4-03b8b792a9bc",
                    "question": "How did food promote long-distance cultural contacts in the pre-modern world ? Explain.",
                    "expanded_syllabus_id": "9415f0bb-61f3-4c7d-871c-b151a9b7ce77",
                    "subtopic": "The silk routes and cultural exchange",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-2-2 Set 2",
                    "marks": "3",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "9bd9770a-2517-47ac-9620-caf310893307",
                    "question": "How is resource planning a complex process ? Explain.",
                    "expanded_syllabus_id": "9442cf47-0307-469f-8226-9bf203456abe",
                    "subtopic": "The importance of resource planning",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 contemporary Set 1",
                    "marks": "3",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "6580b102-2876-4088-9926-0a331f68cb72",
                    "question": "‘‘Sharing of power between the Union Government and State Governments is basic to the structure of our Constitution.’’ Support the statement.",
                    "expanded_syllabus_id": "9a9a14d5-4cd9-4d6f-89a4-08d275a2d284",
                    "subtopic": "Constitutional Amendments and Power Sharing",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-4-2 Set 2",
                    "marks": "3",
                    "imgUrl": null,
                    "metadata": "political science"
                },
                {
                    "id": "11c60aad-eaaa-4382-8451-d7a90d2deb89",
                    "question": "Examine the rising importance of the tertiary sector in India.",
                    "expanded_syllabus_id": "4687e3ca-f3bc-4918-b049-65170a4c18ed",
                    "subtopic": "Rising importance of the tertiary sector",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 32-2-1 Set 1",
                    "marks": "3",
                    "imgUrl": null,
                    "metadata": "economics"
                }
            ]
        },
        {
            "section_name": "Section D",
            "questions": [
                {
                    "id": "ae28a731-63b8-4365-b572-4d36d88130c9",
                    "question": "“The Gandhian idea of Satyagraha, emphasized the power of truth and struggle against injustice.” Explain the statement with examples.",
                    "expanded_syllabus_id": "5d818dc0-10e8-4b23-a90e-7ed8a0f1dd9b",
                    "subtopic": "The concept of Satyagraha",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-2-2 Set 2",
                    "marks": "5",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "1bfbd33a-f720-4d71-9e02-cc03f6323a79",
                    "question": "Explain the features of primitive subsistence and commercial farming in India.",
                    "expanded_syllabus_id": "69e04216-bf03-4de6-bb6d-5aa1582cfe17",
                    "subtopic": "Types of Farming",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 32-2-1 Set 1",
                    "marks": "5",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "abfe870a-accc-4cb8-8435-bc6ddc4283cf",
                    "question": "How does democracy accommodate social diversities ? Explain with \nexamples.",
                    "expanded_syllabus_id": "2971c196-8ed2-4544-a8c0-b7676be7164e",
                    "subtopic": "Accommodation of Social Diversity",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 contemporary Set 1",
                    "marks": "5",
                    "imgUrl": null,
                    "metadata": "political science"
                },
                {
                    "id": "0a902c0a-fbdd-404f-ac63-d7d76660e730",
                    "question": "Explain the difference between organized and unorganized sectors.",
                    "expanded_syllabus_id": "36a052a4-031a-4cfe-b47d-f38f8d986f2d",
                    "subtopic": "Organised and Unorganised sectors",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 contemporary Set 1",
                    "marks": "5",
                    "imgUrl": null,
                    "metadata": "economics"
                }
            ]
        },
        {
            "section_name": "Section E",
            "questions": [
                {
                    "id": "3b93a3a5-66e7-43f3-afbc-19b7136b4720",
                    "question": "Read the following source carefully and answer the questions that follow :\n\nThe earliest factories in England came up by the 1730s. But it was only in the late eighteenth century that the number of factories multiplied.\n\nThe first symbol of the new era was cotton. Its production boomed in the late nineteenth century. In 1760 Britain was importing 2.5 million pounds of raw cotton to feed its cotton industry. By 1787 this import soared to 22 million pounds. This increase was linked to a number of changes within the process of production. Let us look briefly at some of these.\n\nA series of inventions in the eighteenth century increased the efficacy of each step of the production process (carding, twisting and spinning, and rolling). They enhanced the output per worker, enabling each worker to produce more, and they made possible the production of storage threads and yarn. Then Richard Arkwright created the cotton mill. Till this time, as you have seen, cloth production was spread all over the countryside and carried out within village households. But now, the costly new machines could be purchased, set up and maintained in the mill. Within the mill all the processes were brought together under one roof and management. This allowed a more careful supervision over the production process, a watch over quality, and the regulation of labour, all of which had been difficult to do when production was in the countryside.\n(34.1) When did the earliest factories come up ?\n(34.2) Why were all the processes brought together under one roof and management in the mill ?\n(34.3) How did the series of inventions in the eighteenth century increase the efficacy of the production process ?",
                    "expanded_syllabus_id": "081381dd-75a3-4ff7-9283-3a739d8189a1",
                    "subtopic": "The rise of factories in England",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2023",
                    "src": "2023 contemporary Set 1",
                    "marks": "4",
                    "imgUrl": null,
                    "metadata": "history"
                },
                {
                    "id": "4e3e1f52-7c12-4ba9-942f-cf3be90959f6",
                    "question": "Sacred Groves – A wealth of diverse and rare species\nNature worship is an age old tribal belief based on the premise that all creations of nature have to be protected. Such beliefs have preserved several virgin forests in pristine form called Sacred Groves (the forests of God and Goddesses). These patches of forest or parts of large forests have been left untouched by the local people and any interference with them is banned.\nCertain societies revere a particular tree which they have preserved from time immemorial. The Mundas and the Santhal of Chota Nagpur region worship mahua (Bassia latifolia) and kadamba (Anthocaphalus cadamba) trees, and the tribals of Odisha and Bihar worship the tamarind (Tamarindus indica) and mango (mangifera indica) trees during weddings. To many of us, peepal and banyan trees are considered sacred.\nIndian society comprises several cultures, each with its own set of traditional methods of conserving nature and its creations. Sacred qualities are often ascribed to springs, mountain peaks, plants and animals which are closely protected. You will find troops of macaques and langurs around many temples. They are fed daily and treated as a part of temple devotees. In and around Bishnoi villages in Rajasthan, herds of blackbuck, (chinkara), nilgai and peacocks can be seen as an integral part of the community and nobody harms them.\na) How does sacred groves relate to the belief in nature worship?\nb) How do communities incorporate trees into their cultural practices? Explain with example.\nc) Explain the cultural values that contribute to the coexistence of nature.",
                    "expanded_syllabus_id": "986afbe4-cda4-49df-912b-1c929b1f8375",
                    "subtopic": "Sacred Groves",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-3-3 Set 3",
                    "marks": "4",
                    "imgUrl": null,
                    "metadata": "geography"
                },
                {
                    "id": "02f4559b-4d55-4a2a-92c3-d30155c6e96b",
                    "question": "Read the given source and answer the questions that follow :\nSocial and Religious Diversity\nThe Census of India records the religion of each and every Indian after every\nten years. The person who fills the Census form visits every household and\nrecords the religion of each member of that household exactly the way each\nthis is exactly how it is recorded. Thus we have reliable information on the\nproportion of different religious communities in the country and how it has\nchanged over the years. The record shows the population proportion of six major\nreligious communities in the country. Since Independence, the total population of\neach community has increased substantially.\na) At what interval is census conducted in India ?\nb) Why are Indian census data considered reliable ?\nc) How is the census an important tool to understand the social diversity in\nIndia ?",
                    "expanded_syllabus_id": "9a78a332-c94d-43db-b75c-183b8f9c1e93",
                    "subtopic": "Social and Religious Diversity of India",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 contemporary Set 1",
                    "marks": "4",
                    "imgUrl": null,
                    "metadata": "political science"
                }
            ]
        },
        {
            "section_name": "Section F",
            "questions": [
                {
                    "id": "27694277-702c-4e9e-b6a3-6afc212a4a96",
                    "question": "‘‘The French Revolution created a sense of collective identity amongst the French people.’’ Explain the statement with suitable arguments.",
                    "expanded_syllabus_id": "c289bcf8-0b85-4195-beae-a4305c59d039",
                    "subtopic": "The Creation of Collective Identity in France",
                    "difficulty": "Medium",
                    "is_pyq": true,
                    "when_pyq": "2024",
                    "src": "2024 32-4-2 Set 2",
                    "marks": "5",
                    "imgUrl": null,
                    "metadata": "history"
                }
            ]
        }
    ]
}
    
    generate_question_paper_pdf(sample_json, "question_paper.pdf")