from get_stock_sec_form.main import _get_stock_sec_form_html


def test_get_aapl_10k():
    expected_first_10_lines = """<SEC-DOCUMENT>0000320193-20-000096.txt : 20201030
<SEC-HEADER>0000320193-20-000096.hdr.sgml : 20201030
<ACCEPTANCE-DATETIME>20201029180625
ACCESSION NUMBER:		0000320193-20-000096
CONFORMED SUBMISSION TYPE:	10-K
PUBLIC DOCUMENT COUNT:		99
CONFORMED PERIOD OF REPORT:	20200926
FILED AS OF DATE:		20201030
DATE AS OF CHANGE:		20201029
"""
    expected_last_10_lines = """M 0 !E@( %               @ %#P00 86%P;"TR,#(P,#DR-E]G,BYJ<&=0
M2P$"% ,4    " #)D%U1ZE:6M<)8 0#.O0T %0              @ %D@08
M86%P;"TR,#(P,#DR-E]L86(N>&UL4$L! A0#%     @ R9!=443SH2\QOP
MY,,( !4              ( !6=H' &%A<&PM,C R,# Y,C9?<')E+GAM;%!+
4!08     $  0 $\$  "]F0@    !

end
</TEXT>
</DOCUMENT>
</SEC-DOCUMENT>"""

    aapl_10k_html = _get_stock_sec_form_html("aapl", "10-k")
    fetched_first_10_lines = "\n".join(aapl_10k_html.splitlines()[:10])
    fetched_last_10_lines = "\n".join(aapl_10k_html.splitlines()[-10:])

    assert fetched_first_10_lines == expected_first_10_lines
    assert fetched_last_10_lines == expected_last_10_lines
