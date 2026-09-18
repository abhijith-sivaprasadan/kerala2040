from kerala2040.generators import generator_database


def test_generator_database_does_not_infer_owner():
    projects = {
        "tracker": {"data_as_of_label": "old"},
        "projects": [
            {
                "name": "Example HEP",
                "technology": "Hydro",
                "status": "Completed",
                "capacity_mw": 10.0,
                "district": "Idukki",
                "milestone_date_label": "12, Feb 2001",
            }
        ],
    }
    observed = {
        "electricity": {
            "installed_capacity_mw": 100.0,
            "capacity_mix_mw": {
                "hydel": 50.0,
                "thermal": 20.0,
                "solar": 25.0,
                "wind": 5.0,
            },
        }
    }
    frame, summary = generator_database(projects, observed)

    assert frame.loc[0, "commissioning_year"] == 2001
    assert frame.loc[0, "owner"] is None
    assert summary["official_total_installed_capacity_mw"] == 100.0
