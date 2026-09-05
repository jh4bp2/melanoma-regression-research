from app.corpus.collection_recovery import recover_collections
from app.corpus.episode_canonical import canonicalize_episodes, should_split_collapsed_case
from app.corpus.lesion_naming import improved_lesion_name, is_weak_lesion_name
from app.corpus.polarity import (
    DirectionPolarity,
    PolarityDecision,
    check_claim_against_quote,
    polarity_of,
)
from app.corpus.versions import CORPUS_INFRA_VERSION, CORPUS_RULE_VERSION, frozen_ontology
from app.models import (
    CollectionMembershipStatus,
    LesionScopeKind,
    RegressionEpisode,
    RegressionEpisodeType,
    RegressionExtent,
)


class _Lesion:
    def __init__(self, lesion_id, name, organ=None, location=None):
        self.id = lesion_id
        self.canonical_name = name
        self.organ = organ
        self.anatomical_location = location


def _episode(episode_id, index, description, extent="UNCERTAIN", lesions=None, case_id=1):
    return RegressionEpisode(
        id=episode_id,
        paper_id=1,
        case_id=case_id,
        episode_index=index,
        episode_type=RegressionEpisodeType.SPONTANEOUS,
        extent=RegressionExtent(extent),
        associated_lesion_ids=lesions or [],
        associated_event_ids=[],
        description=description,
    )


def test_corpus_patch_versions_keep_phase34():
    frozen = frozen_ontology()
    assert frozen["corpus_infra_version"] == "phase4a.2"
    assert frozen["corpus_rule_version"] == "phase4a2-collection-episode-v1"
    assert frozen["phase2_schema"] == "phase2.3"
    assert frozen["phase3_schema"] == "phase3.4"
    assert frozen["phase3_prompt"] == "biological_observation_extraction:v5"
    assert CORPUS_INFRA_VERSION == "phase4a.2"
    assert CORPUS_RULE_VERSION == "phase4a2-collection-episode-v1"


def test_multiple_lung_metastases_become_collection_only():
    recovered = recover_collections(
        [("multiple lung metastases", "CT revealed multiple lung metastases", 1)],
        [],
    )
    assert len(recovered) == 1
    assert recovered[0].organ == "LUNG"
    assert recovered[0].collection_type == LesionScopeKind.METASTATIC_LESION_GROUP
    assert recovered[0].membership_status == CollectionMembershipStatus.COLLECTION_ONLY
    assert recovered[0].member_lesion_ids == []


def test_multiple_lymph_nodes_become_collection():
    recovered = recover_collections(
        [("multiple lymph-node metastases", "multiple lymph node metastases", 2)],
        [],
    )
    assert recovered[0].organ == "LYMPH_NODE"
    assert recovered[0].membership_status == CollectionMembershipStatus.COLLECTION_ONLY


def test_multiple_nevi_become_collection():
    recovered = recover_collections(
        [("all her nevi had disappeared", "all the nevi, but not lentigines, had disappeared", 3)],
        [],
    )
    assert recovered[0].collection_type == LesionScopeKind.MELANOCYTIC_NEVI_GROUP
    assert recovered[0].membership_status == CollectionMembershipStatus.COLLECTION_ONLY


def test_explicit_brain_lesions_stay_individual():
    lesions = [
        _Lesion(1, "right fronto-parietal brain metastasis", "BRAIN", "FRONTO_PARIETAL"),
        _Lesion(2, "left frontal brain metastasis", "BRAIN", "FRONTAL"),
    ]
    recovered = recover_collections(
        [
            (
                "right fronto-parietal brain metastasis 46/37 mm",
                "axial diameter of 46/37 mm in right fronto-parietal area",
                4,
            ),
            (
                "left frontal brain metastasis 36/35 mm",
                "36/35 mm in left frontal area",
                5,
            ),
        ],
        lesions,
    )
    assert not any(item.organ == "BRAIN" for item in recovered)


def test_case_and_lesion_provenance_survives_episode_merge():
    episodes = [
        _episode(11, 1, "The thigh lesion disappeared after FNA.", lesions=[116], case_id=31),
        _episode(12, 2, "CT scans did not reveal the lesion.", lesions=[116], case_id=31),
    ]
    canonical = canonicalize_episodes(episodes, lesion_organs={116: "SKIN"})
    assert len(canonical) == 1
    assert canonical[0].case_id == 31
    assert canonical[0].associated_lesion_ids == [116]
    assert canonical[0].source_episode_ids == [11, 12]


def test_partial_membership_does_not_invent_phantoms():
    lesions = [_Lesion(9, "right lower lobe nodule", "LUNG", "LOWER_LOBE")]
    recovered = recover_collections(
        [
            (
                "multiple pulmonary metastases, one dominant right lower lobe lesion",
                "multiple pulmonary metastases, one dominant right lower lobe lesion",
                6,
            )
        ],
        lesions,
    )
    assert len(recovered) == 1
    assert recovered[0].member_lesion_ids == [9]
    assert recovered[0].membership_status == CollectionMembershipStatus.PARTIAL_MEMBERS_KNOWN


def test_unrelated_lesion_is_not_attached_to_collection():
    lesions = [
        _Lesion(9, "right lower lobe nodule", "LUNG", "LOWER_LOBE"),
        _Lesion(99, "left inguinal node", "LYMPH_NODE", "INGUINAL"),
    ]
    recovered = recover_collections(
        [
            (
                "multiple pulmonary metastases, one dominant right lower lobe lesion",
                "multiple pulmonary metastases, one dominant right lower lobe lesion",
                6,
            )
        ],
        lesions,
    )
    assert recovered[0].member_lesion_ids == [9]
    assert 99 not in recovered[0].member_lesion_ids


def test_discussion_statement_does_not_create_collection():
    recovered = recover_collections(
        [
            (
                "It is estimated that 35% of spontaneous tumor regression occurs",
                "It is estimated that 35% of spontaneous tumor regression occurs",
                7,
            )
        ],
        [],
    )
    assert recovered == []


def test_continuous_regression_episodes_merge():
    episodes = [
        _episode(1, 1, "The lesion disappeared after FNA and was considered spontaneous."),
        _episode(2, 2, "CT scans did not reveal the lesion."),
        _episode(3, 3, "Follow-up ultrasound did not detect any tumor."),
    ]
    canonical = canonicalize_episodes(episodes)
    assert len(canonical) == 1
    assert canonical[0].action == "MERGED"
    assert len(canonical[0].source_episode_ids) == 3
    assert {row["label"] for row in canonical[0].milestones} >= {
        "complete_disappearance",
        "confirmation",
    }


def test_partial_to_complete_same_process_merges():
    episodes = [
        _episode(
            1,
            1,
            "The right-sole lesion recently decreased in size.",
            extent="PARTIAL",
        ),
        _episode(
            2,
            2,
            "Complete regression of primary cutaneous melanoma on the right sole.",
            extent="COMPLETE",
        ),
    ]
    canonical = canonicalize_episodes(episodes)
    assert len(canonical) == 1
    assert canonical[0].extent == "COMPLETE"
    assert canonical[0].extent_transition == "PARTIAL_TO_COMPLETE"


def test_true_separate_organ_episodes_are_preserved():
    episodes = [
        _episode(1, 1, "Spontaneous regression of the right heel primary.", lesions=[1]),
        _episode(2, 2, "Later the axillary in-transit metastases resolved.", lesions=[2]),
    ]
    canonical = canonicalize_episodes(episodes, lesion_organs={1: "SKIN", 2: "LYMPH_NODE"})
    assert len(canonical) == 2


def test_recurrence_then_second_regression_stays_separate():
    episodes = [
        _episode(1, 1, "The thigh nodules resolved spontaneously."),
        _episode(2, 2, "After recurrence a second regression of new nodules occurred."),
    ]
    canonical = canonicalize_episodes(episodes)
    assert len(canonical) == 2


def test_collapsed_mixed_course_can_split():
    episodes = [_episode(1, 1, "Neck recurrence then mixed pulmonary nodule course.")]
    assert should_split_collapsed_case(episodes, ["LYMPH_NODE", "LUNG"]) == [
        "LUNG",
        "LYMPH_NODE",
    ]


def test_remained_is_not_disappeared():
    result = check_claim_against_quote(
        "lentigines remained",
        "lentigines disappeared",
        subject="lentigines",
    )
    assert result.decision == PolarityDecision.FACT_INVERSION
    assert polarity_of("persisted") == DirectionPolarity.PERSISTENCE
    assert polarity_of("resolved") == DirectionPolarity.DISAPPEARANCE


def test_but_not_lentigines_blocks_disappearance_claim():
    quote = (
        "all the nevi, but not lentigines (epidermal hyperplasia with increased "
        "keratinocytes), had disappeared leaving a white pigmentation"
    )
    result = check_claim_against_quote(
        quote,
        "lentigines had disappeared",
        subject="lentigines",
    )
    assert result.decision == PolarityDecision.FACT_INVERSION


def test_did_not_regress_negation():
    assert polarity_of("the mass did not regress") == DirectionPolarity.NEGATED_DISAPPEARANCE
    result = check_claim_against_quote(
        "the mass did not regress",
        "the mass disappeared",
    )
    assert result.decision == PolarityDecision.FACT_INVERSION


def test_no_viable_tumor_scope_is_absent():
    assert polarity_of("no viable tumor cells") == DirectionPolarity.ABSENT
    result = check_claim_against_quote(
        "no viable tumor cells were seen",
        "viable melanoma cells present",
    )
    assert result.decision == PolarityDecision.FACT_INVERSION


def test_source_polarity_ok_when_aligned():
    result = check_claim_against_quote(
        "all the nevi had disappeared",
        "cutaneous nevi disappearance",
        subject="nevi",
    )
    assert result.decision == PolarityDecision.OK


def test_weak_lesion_name_can_improve_from_thigh_evidence():
    assert is_weak_lesion_name("right mass")
    improved = improved_lesion_name(
        "right mass",
        [
            "resection of the tumor on his right ankle",
            "hypoechoic tubular structure in the subcutaneous layer of the right thigh",
        ],
        forbidden_names=["right ankle lesion"],
    )
    assert improved is not None
    assert "thigh" in improved
    assert "ankle" not in improved
    assert improved_lesion_name("right inguinal lymph node", ["right thigh mass"]) is None


def test_normal_liver_scan_does_not_create_hepatic_collection():
    recovered = recover_collections(
        [
            (
                "Several pulmonary nodules were visible in both lungs; liver scan were normal.",
                "Several pulmonary nodules were visible in both lungs on chest X-ray; physical examination and liver scan were normal.",
                9,
            )
        ],
        [],
    )
    assert any(item.organ == "LUNG" for item in recovered)
    assert not any(item.organ == "LIVER" for item in recovered)


def test_negated_bone_metastases_do_not_create_collection():
    recovered = recover_collections(
        [("No bones metastases were seen", "No bones metastases were seen", 8)],
        [],
    )
    assert not any(item.organ == "BONE" for item in recovered)
