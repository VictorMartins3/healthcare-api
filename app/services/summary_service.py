import json
from datetime import date
from anthropic import Anthropic
from app.core.config import settings
from app.models.patient import Patient


class SummaryService:
    @staticmethod
    def _calculate_age(date_of_birth: date) -> int:
        today = date.today()
        return today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )

    @staticmethod
    def _demo_summary(patient: Patient, notes: list, audience: str) -> tuple:
        if not notes:
            return ("No clinical notes available for this patient.", ["No documented findings"])

        age = SummaryService._calculate_age(patient.date_of_birth)
        count = len(notes)
        start = notes[0].taken_at.strftime('%Y-%m-%d')
        end = notes[-1].taken_at.strftime('%Y-%m-%d')

        if audience == "family":
            summary = f"{patient.name} is a {age}-year-old patient with {count} visit(s) between {start} and {end}."
            findings = [f"{count} visits documented", "Regular care ongoing"]
        else:
            summary = f"Patient {patient.name} (MRN: {patient.mrn}), {age}yo. {count} note(s) from {start} to {end}."
            findings = [f"{count} clinical notes", f"Age: {age}", f"Period: {start} to {end}"]

        return summary, findings

    @staticmethod
    async def generate_summary(patient: Patient, notes: list, audience: str = "clinician") -> tuple:
        if not settings.anthropic_api_key:
            return SummaryService._demo_summary(patient, notes, audience)

        if not notes:
            return ("No clinical notes available for this patient.", ["No documented findings"])

        age = SummaryService._calculate_age(patient.date_of_birth)
        notes_context = "\n\n".join([
            f"Note ({note.taken_at.strftime('%Y-%m-%d')}):\n{note.content}" for note in notes
        ])

        tone = "non-technical, family-friendly" if audience == "family" else "clinical, professional"

        prompt = f"""Generate a patient summary.

Patient: {patient.name}, {age}yo, MRN: {patient.mrn}

Notes:
{notes_context}

Provide a {tone} summary. Return JSON:
{{"summary": "...", "key_findings": ["...", "..."]}}"""

        client = Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            result = json.loads(response.content[0].text)
            return result.get("summary", ""), result.get("key_findings", [])
        except json.JSONDecodeError:
            return response.content[0].text, ["See summary"]
