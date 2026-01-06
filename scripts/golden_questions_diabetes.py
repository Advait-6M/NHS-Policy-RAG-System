"""
Golden Questions and Ground Truth for Diabetes-Focused RAG Evaluation.

These questions are specifically designed to test retrieval and generation
capabilities for the NHS diabetes policy documents in the knowledge base.
"""

GOLDEN_QUESTIONS = [
    {
        "question": "What are the NICE recommendations for using SGLT2 inhibitors like Dapagliflozin in patients with Type 2 Diabetes and heart failure?",
        "ground_truth": "According to NICE guidance, SGLT2 inhibitors with proven cardiovascular benefit are recommended for adults with Type 2 Diabetes who have chronic heart failure or established atherosclerotic cardiovascular disease. Dapagliflozin is specifically recommended for treating chronic heart failure with reduced ejection fraction (HFrEF) and heart failure with preserved or mildly reduced ejection fraction (HFpEF). The dose is 10mg once daily, which can be taken with or without food. Primary care clinicians should prescribe these medications on the advice of a heart failure specialist.",
        "topic": "SGLT2 Inhibitors - Heart Failure"
    },
    {
        "question": "What are the eligibility criteria for continuous glucose monitoring (CGM) in Type 2 Diabetes?",
        "ground_truth": "According to NICE guidelines, continuous glucose monitoring (CGM) is recommended for adults with Type 2 Diabetes who have a high risk of developing cardiovascular disease. This includes those with QRISK3 more than 10% in adults aged 40 and over, or an elevated lifetime risk of cardiovascular disease (defined as the presence of 1 or more cardiovascular risk factors in someone under 40). For patients using insulin, eligible criteria for CGM are available at NetFormulary. Local Specialist Diabetes Teams will advise Primary Care for individual patients with complex clinical needs.",
        "topic": "Continuous Glucose Monitoring"
    },
    {
        "question": "When should Tirzepatide be prescribed for Type 2 Diabetes according to local CPICS guidance?",
        "ground_truth": "Tirzepatide can be prescribed for Type 2 Diabetes according to NICE TA924 criteria. It can be prescribed by both primary care and secondary care clinicians for patients who meet the eligibility criteria. When used with SGLT2 inhibitor therapy, the current dose of metformin and/or SGLT2i can be continued. Tirzepatide is a GLP-1 receptor agonist that should be considered when other treatments have not been effective after six months.",
        "topic": "Tirzepatide Prescribing"
    },
    {
        "question": "What are the key safety considerations when prescribing SGLT2 inhibitors for diabetes?",
        "ground_truth": "Key safety considerations for SGLT2 inhibitors include: 1) Hypoglycemia risk - requires dose reduction of insulin and/or sulphonylureas when starting SGLT2i; 2) Diabetic ketoacidosis (DKA) - follow 'sick day' rules, withhold during concomitant illness or surgery, maintain fluid and carbohydrate intake, and measure blood ketones even if blood sugar is in normal range; 3) The team performing planned operations should advise patients on whether SGLT2 inhibitor treatment should be stopped and when. Rare cases of DKA have been reported, and if suspected or diagnosed, the medication should be stopped immediately.",
        "topic": "SGLT2 Inhibitor Safety"
    },
    {
        "question": "What are the NICE recommendations for blood glucose self-monitoring in Type 2 Diabetes?",
        "ground_truth": "According to NICE and local CPICS guidance, blood glucose self-monitoring recommendations depend on the medication: For medications without hypoglycemia risk (Metformin, DPP-4 inhibitors, GLP-1 agonists, SGLT2 inhibitors, Pioglitazone) - do not offer self-monitoring. For Sulphonylureas: maintenance requires 2-3 times per week at different times; initiation and titration requires 2-3 times per week; drivers must test within 2 hours before driving and every 2 hours whilst driving. For insulin users, continuous glucose monitoring (CGM) eligibility criteria are available at NetFormulary.",
        "topic": "Blood Glucose Monitoring"
    },
    {
        "question": "What is the Individual Funding Request (IFR) process for diabetes medications not routinely commissioned?",
        "ground_truth": "The IFR process allows clinicians to request funding for treatments not routinely commissioned. NHS England will consider funding if: 1) There is evidence of exceptional clinical circumstances; 2) There is relevant NHS clinical commissioning policy, NICE Technology Appraisal guidance, or other mandatory guidance; 3) The patient presents differently from the general population. The IFR Panel reviews requests and makes decisions based on clinical exceptionality. If declined, clinicians can submit new clinical evidence for reconsideration. The process excludes days spent awaiting information from the requester.",
        "topic": "Individual Funding Requests"
    },
    {
        "question": "When should adults with Type 2 Diabetes be offered structured education programmes?",
        "ground_truth": "According to NICE guidelines, structured education programmes should be offered to adults with Type 2 Diabetes and their family members or carers at the time of diagnosis, with annual reinforcement and review. The programme should be evidence-based, suit the person's needs, and be delivered by trained educators. Adults with Type 2 Diabetes should have the opportunity to contribute to the design and provision of local education programmes. The programmes should be integrated with the rest of the care pathway.",
        "topic": "Diabetes Education"
    },
    {
        "question": "What are the recommendations for using Dapagliflozin in patients with chronic kidney disease and diabetes?",
        "ground_truth": "According to NICE TA775, Dapagliflozin is recommended for treating chronic kidney disease (CKD) in adults, but only if: 1) It is an add-on to optimised standard care including the highest tolerated licensed dose of ACE inhibitors or ARBs (unless contraindicated); AND 2) People have an eGFR of 25-75 ml/min/1.73m² at the start of treatment; AND 3) They have type 2 diabetes OR have a urine albumin-to-creatinine ratio (uACR) of 22.6 mg/mmol or more. Primary care clinicians can prescribe for CKD patients who meet these criteria. A local pathway is available to support prescribers.",
        "topic": "Dapagliflozin - Chronic Kidney Disease"
    },
    {
        "question": "What are the NICE recommendations for triple therapy in Type 2 Diabetes management?",
        "ground_truth": "According to NICE guidelines, if dual therapy with metformin and another oral drug has not controlled HbA1c to below the person's individually agreed threshold, consider triple therapy by adding: a DPP-4 inhibitor, pioglitazone, a sulfonylurea, or an SGLT2 inhibitor for people who meet the criteria in NICE's technology appraisal guidance. Alternatively, consider starting insulin-based treatment. The choice should be individualized based on the person's clinical circumstances, preferences, and cardiovascular risk profile.",
        "topic": "Triple Therapy"
    },
    {
        "question": "What is the recommended dosing and administration for Empagliflozin in heart failure patients with diabetes?",
        "ground_truth": "For heart failure patients (both HFrEF and HFpEF), Empagliflozin is dosed at 10mg once daily, which can be taken with or without food. There is no dose adjustment required based on the type of heart failure. Primary care clinicians will be asked to prescribe Empagliflozin for heart failure patients only on the advice of a heart failure specialist. Eligible patients will be identified through cardiology and heart failure clinics, hospital admission, and community heart failure specialist nursing teams, meeting inclusion criteria in keeping with NICE TA773 or TA929.",
        "topic": "Empagliflozin - Heart Failure"
    }
]


def get_golden_questions():
    """Return the list of golden questions for evaluation."""
    return GOLDEN_QUESTIONS


def get_question_topics():
    """Return unique topics covered by golden questions."""
    return list(set(q["topic"] for q in GOLDEN_QUESTIONS))


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DIABETES-FOCUSED GOLDEN QUESTIONS")
    print("=" * 80)
    print(f"\nTotal Questions: {len(GOLDEN_QUESTIONS)}")
    print(f"Topics Covered: {', '.join(get_question_topics())}\n")
    
    for i, q in enumerate(GOLDEN_QUESTIONS, 1):
        print(f"\n{i}. {q['question']}")
        print(f"   Topic: {q['topic']}")
        print(f"   Ground Truth Length: {len(q['ground_truth'])} chars")

