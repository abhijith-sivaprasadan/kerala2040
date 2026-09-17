from __future__ import annotations

from kerala2040.sources.sldc import parse_system_statistics

HTML = """
<html><body>
<h1>SYSTEM STATISTICS - FOR  16/09/2026 ,Wednesday</h1>
<table>
<tr><td> Hydel Total</td><td>24.4575</td><td>373.5461</td></tr>
<tr><td> Internal Generation</td><td>26.8683</td><td>416.9098</td></tr>
<tr><td> Net Import</td><td>68.9468</td><td>1081.9224</td></tr>
<tr><td> Consumption </td><td>95.8151</td><td>1498.8322</td></tr>
<tr><td> Import (mu)</td><td>4.433</td></tr>
<tr><td> Export (mu)</td><td>0.586</td></tr>
<tr><td> Net Import (on UI) (mu)</td><td>3.847</td></tr>
</table>
</body></html>
"""


def test_parse_sldc_keeps_interface_and_ui_import_separate():
    result = parse_system_statistics(HTML)
    assert result["report_date"] == "2026-09-16"
    assert result["metrics"]["internal_generation_mu"] == 26.8683
    assert result["metrics"]["net_import_interface_mu"] == 68.9468
    assert result["metrics"]["ui_net_import_mu"] == 3.847
    assert abs(result["balance_error_mu"]) < 1e-9
