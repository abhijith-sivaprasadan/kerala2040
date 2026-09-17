from kerala2040.sources.sldc_storage import parse_storage

HTML = """
<html><body>
<h1 class="title">SYSTEM STATISTICS: STORAGE AS ON  01.04.2025</h1>
<table class="display">
<tr><td>header</td></tr>
<tr>
<td>694.944</td><td>732.43</td><td>1460</td><td>2190</td><td>IDUKKI</td>
<td>720.0</td><td>850</td><td>58</td><td>1200</td><td>1175</td>
<td>4</td><td>0</td><td>3.5</td><td>10.5</td><td>57</td><td>remark</td>
</tr>
</table>
</body></html>
"""


def test_parse_storage() -> None:
    parsed = parse_storage(HTML)
    assert parsed["report_date"] == "2025-04-01"
    assert parsed["reservoirs"][0]["reservoir"] == "IDUKKI"
    assert parsed["system"]["full_storage_mu"] == 2190.0
    assert parsed["system"]["generation_capability_gross_mu"] == 1200.0
