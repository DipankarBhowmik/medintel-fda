import streamlit as st
from medintel.medlineplus import search_medlineplus
from medintel.openfda import fetch_drug_label
from medintel.ai_processing import analyze_medical_text

def main():
    st.title("🩺 MedIntelAI: MedlinePlus & OpenFDA Explorer")

    tab1, tab2 = st.tabs(["🔎 MedlinePlus Search", "💊 OpenFDA Drugs"])

    if "drug_list" not in st.session_state:
        st.session_state["drug_list"] = []

    with tab1:
        disease = st.text_input("🔎 Search Disease", value="migraine")

        if st.button("Search"):
            st.info(f"Searching MedlinePlus for **{disease}** ...")
            results = search_medlineplus(disease)

            if not results:
                st.error("No results found.")
                return

            final_summary, cleaned_list = analyze_medical_text(disease, results, st)
            st.session_state["drug_list"] = cleaned_list

            st.subheader("📌 Final Summary")
            st.write(final_summary)
            st.subheader("🔑 Main Medicine(s)")
            st.write(", ".join(cleaned_list) if cleaned_list else "No valid medicines found.")

    with tab2:
        st.write("FDA-approved drug details:")
        cleaned_list = st.session_state.get("drug_list", [])

        if not cleaned_list:
            st.warning("⚠️ No drugs found yet. Please search in MedlinePlus first.")
        else:
            for d_name in cleaned_list:
                st.subheader(f"💊 {d_name}")
                results = fetch_drug_label(d_name)
                if results:
                    for drug in results:
                        st.markdown(f"""
                        **Brand Name:** {", ".join(drug.get("openfda", {}).get("brand_name", ["N/A"]))}  
                        **Generic Name:** {", ".join(drug.get("openfda", {}).get("generic_name", ["N/A"]))}  
                        **Manufacturer:** {", ".join(drug.get("openfda", {}).get("manufacturer_name", ["N/A"]))}  
                        **Purpose:** {" ".join(drug.get("purpose", ["N/A"]))}  
                        **Indications & Usage:** {" ".join(drug.get("indications_and_usage", ["N/A"]))}  
                        """)
                        st.markdown("---")
                else:
                    st.error(f"No results found for {d_name}.")

if __name__ == "__main__":
    main()
