#!/bin/bash

EXPECTED_HEADERS="folio,folio_display,div_id,categories,heading_tc,heading_tcn,heading_tl,al_tc,al_tcn,al_tl,bp_tc,bp_tcn,bp_tl,cn_tc,cn_tcn,cn_tl,df_tc,df_tcn,df_tl,env_tc,env_tcn,env_tl,m_tc,m_tcn,m_tl,md_tc,md_tcn,md_tl,ms_tc,ms_tcn,ms_tl,mu_tc,mu_tcn,mu_tl,pa_tc,pa_tcn,pa_tl,pl_tc,pl_tcn,pl_tl,pn_tc,pn_tcn,pn_tl,pro_tc,pro_tcn,pro_tl,sn_tc,sn_tcn,sn_tl,tl_tc,tl_tcn,tl_tl,tmp_tc,tmp_tcn,tmp_tl,wp_tc,wp_tcn,wp_tl,de_tc,de_tcn,de_tl,el_tc,el_tcn,el_tl,it_tc,it_tcn,it_tl,la_tc,la_tcn,la_tl,oc_tc,oc_tcn,oc_tl,po_tc,po_tcn,po_tl"


if [ "$EXPECTED_HEADERS" != "$(cat ./metadata/entry_metadata.csv | head -1)" ] ;
then
    echo "error: entry_metadata.csv has missing headings:" >&2
    echo "$(sdiff <(echo "$EXPECTED_HEADERS") <(echo "$(cat ./metadata/entry_metadata.csv | head -1)"))" >&2
    exit 2
fi

