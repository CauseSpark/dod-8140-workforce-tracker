# DoD 8140 in Brief

> Plain-language summary written for this portfolio project. It is **not** official
> guidance. Always read the primary sources linked at the bottom.
> Status checked: **November 11, 2026**.

## 1. From 8570 to 8140

For about two decades, DoD 8570.01-M was the main way the DoD qualified its
information assurance workforce. It grouped people into broad categories
(IAT, IAM, IASAE, CSSP) and qualified them mostly by holding an approved
baseline certification.

**DoD Manual 8140.03, *Cyberspace Workforce Qualification and Management Program*,
was signed on February 15, 2023, and it cancelled DoD 8570.01-M.** It sits
under DoD Directive 8140.01 (Cyberspace Workforce Management) and DoDI 8140.02
(Identification, Tracking, and Reporting of Cyberspace Workforce Requirements).

The main differences:

| | DoD 8570.01-M (cancelled) | DoDM 8140.03 (current) |
|---|---|---|
| Scope | IA / computer network defense workforce | Whole cyberspace workforce (IT, cybersecurity, cyber effects, cyber intelligence, cyber enablers, and newer elements) |
| Unit of qualification | Category + level (e.g., IAT II) | DCWF **work role** + **proficiency level** |
| Primary evidence | Baseline certification | Several paths: education, training, certification, or documented experience, **plus** on-the-job (residential) qualification |
| Flexibility | Mostly fixed list | Components may add their own requirements |

## 2. The work-role approach

8140 is built on the **DoD Cyber Workforce Framework (DCWF)**. Each position is
coded to one or more DCWF work roles, for example *511 Cyber Defense Analyst*
or *722 Information Systems Security Manager*. Each work role has:

- a three-digit code and a workforce element (cybersecurity, IT, cyber enabler, and so on);
- a defined set of Knowledge, Skills, Abilities, and Tasks (KSATs); and
- a required **proficiency level** for the position: **Basic, Intermediate, or Advanced**.

The person is qualified against the *role and level of the position*, not a
generic certification ladder. This repository's tracker models that: each
person has an assigned `dcwf_code` and `proficiency_level`.

## 3. Qualification types

DoDM 8140.03 splits qualification into parts. This project models the first two.

**Foundational qualification** shows that the person has baseline knowledge for
the work role. A person meets it through **one** option listed in the official
qualification matrix for their role and level:

- **Education**: an accredited degree in a listed discipline
- **Training**: a listed course (for example, DCWF learning playlists)
- **Personnel certification**: a listed, accredited certification
- **Experience**: documented on-the-job experience, using the official experience
  qualification process

The official matrix guidance also says an option aligned at a higher proficiency
level satisfies lower levels. `src/role_gap_report.py` applies the same rule.

**Residential qualification** shows that the person can do the work in *this*
job and environment. Examples are on-the-job evaluation, environment-specific
training, or a command-specified certification. The Component defines it, and
the tracker records it as a Y/N flag.

**Continuous professional development / continuous learning** keeps people
current after they qualify. Certification renewal is a separate clock from
DoD continuous learning. A certification that lapses can take away the
foundational qualification it was providing. That is why
`src/expiry_check.py` exists.

## 4. Implementation timeline (high level)

| Date | Milestone |
|---|---|
| Feb 15, 2023 | DoDM 8140.03 signed; DoD 8570.01-M cancelled |
| Feb 15, 2025 | Cybersecurity workforce element qualification deadline (foundational) |
| Feb 15, 2026 | Deadline for cyber IT, cyber effects, cyber (intelligence), and cyber enabler elements (foundational); cybersecurity residential |
| Feb 15, 2027 | Residential deadline for the remaining elements |

Check the official implementation timeline below for exact wording and scope.

## 5. Qualification matrix status

As of the date above, the current version is the **DoD 8140 Foundational
Qualification Matrix V2.1, effective September 19, 2025**. The official
qualification-matrices page lists V2.0 (March 25, 2025) as an archive version.
The matrix is updated periodically, so check it before you rely on any mapping.

## Primary sources

- DoD 8140 program home (DoD CIO / DoW CIO): <https://www.cyberworkforce.mil/DoD-8140/>
- DoD 8140 Qualification Matrices (DoD Cyber Exchange): <https://www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices>
- Sample DCWF Work Role Qualification Matrix: <https://www.cyberworkforce.mil/DoD-8140/Sample-DCWF-Work-Role-Qualification-Matrix/>
- DoDM 8140.03 (WHS Directives Division): <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodm/814003p.PDF>
- DoD Cyber Workforce Development: <https://dodcio.defense.gov/Cyber-Workforce/DoDCW.aspx>
- DoD 8140 Implementation Timeline (PDF): <https://dodcio.defense.gov/Portals/0/Documents/Cyber/DoD8140-ImplementationTimeline.pdf>
