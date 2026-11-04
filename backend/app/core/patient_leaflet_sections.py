from dataclasses import dataclass


@dataclass(frozen=True)
class PatientLeafletSection:
    number: int
    title: str


PATIENT_LEAFLET_SECTIONS = (
    PatientLeafletSection(1, "Para que este medicamento é indicado?"),
    PatientLeafletSection(2, "Como este medicamento funciona?"),
    PatientLeafletSection(3, "Quando não devo usar este medicamento?"),
    PatientLeafletSection(4, "O que devo saber antes de usar este medicamento?"),
    PatientLeafletSection(5, "Onde, como e por quanto tempo posso guardar este medicamento?"),
    PatientLeafletSection(6, "Como devo usar este medicamento?"),
    PatientLeafletSection(7, "O que devo fazer quando eu me esquecer de usar este medicamento?"),
    PatientLeafletSection(8, "Quais os males que este medicamento pode me causar?"),
    PatientLeafletSection(9, "O que fazer se alguém usar uma quantidade maior do que a indicada deste medicamento?"),
)

SECTION_TITLES_BY_NUMBER = {section.number: section.title for section in PATIENT_LEAFLET_SECTIONS}
