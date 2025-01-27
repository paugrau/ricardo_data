import json
import os
import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


try:
    conf = json.load(open("config.json", "r"))
    database_filename = os.path.join('../sqlite_data', conf["sqlite_viz"])
except:
    print "couldn't load config.json database"
    exit(1)


conn = sqlite3.connect(database_filename)
conn.row_factory = dict_factory
cursor = conn.cursor()

#KEY_TO_INSERT = ['source_label','original_reporting','currency','rate','year','partner','expimp','quality_tag','unit','reporting_continent','reporting_part_of_GPH_entity','source','type','reporting_slug','reporting','original_partner','species_bullions','partner_type','partner_continent','partner_slug','spegen','reporting_type','notes','flow','partner_part_of_GPH_entity','transport_type']

with open('group_desaggregations.json', 'r') as f:
    group_desaggregations = json.load(f)
    # applying the patch on the bdd table
    sql_updates_values = []
    sql_updates_keys = []
    sql_inserts_values = []
    sql_inserts_keys = []

    ids_to_delete = []
    partners_to_complete = []

    for desagg in group_desaggregations:
        id_flow = desagg['group_flow']['id']
        for new_flow in (d for d in desagg['new_flows'] if 'negative' not in d['quality_tag']):
            # copy original flow data
            insert_data = desagg['group_flow'].copy()
            # apply the new flow value to it
            insert_data.update(new_flow)
            # remove id
            del(insert_data['id'])
            if len(insert_data.keys()) != 26:
                print len(insert_data.keys())
            else:
                sql_inserts_keys = insert_data.keys()  # always the same... this is bad
                sql_inserts_values.append(insert_data.values())

        if desagg['delete_group_flow']:
            ids_to_delete.append([id_flow])
        elif desagg['update'] != {} and 'negative' not in desagg['update']['quality_tag']:
            if desagg['update']['quality_tag'] == 'group_desaggregation_total':
                partners_to_complete.append(desagg['update']['partner'])
            sql_updates_keys = desagg['update'].keys()
            sql_updates_values.append(desagg['update'].values()+[id_flow])

    cursor.execute(
        """SELECT count(distinct partner) FROM flow_aggregated where partner_type = 'group'""")
    print "reducing %s partner groups " % cursor.fetchone()
    cursor.execute(
        """SELECT count(*) FROM flow_aggregated where partner_type = 'group'""")
    print "reducing %s flows with partner groups " % cursor.fetchone()

    cursor.executemany("""INSERT INTO flow_aggregated ("%s") VALUES (%s)""" % ('","'.join(sql_inserts_keys), ','.join('?' for _ in range(26))),
                       sql_inserts_values)
    print "inserted %s new flows to disaggregated entities from groups" % cursor.rowcount

    cursor.executemany("""UPDATE flow_aggregated SET %s WHERE id=?""" % ','.join(
        '%s=?' % k for k in sql_updates_keys), sql_updates_values)
    print "updated %s flows containing a group entitiy partner" % cursor.rowcount

    partners_to_complete_values = []
    partners_to_complete_keys = ['type', 'continent', 'part_of_GPH_entity']

    # add RICname metadata to partner column in flows for new bilateral flows to desaggregated entities from group
    cursor.execute("""SELECT * from RICentities """)
    for partner in cursor:
        partners_to_complete_values.append([v for k, v in partner.iteritems(
        ) if k in partners_to_complete_keys] + [partner['RICname']])

    cursor.executemany("""UPDATE flow_aggregated SET %s WHERE partner=?""" % ','.join('"partner_%s"=?' % k for k in partners_to_complete_keys),
                       partners_to_complete_values)
    print "Added metadata to %s  partner desaggregated from group" % len(partners_to_complete)

    cursor.executemany(
        """DELETE FROM flow_aggregated WHERE id=?""", ids_to_delete)
    print "Deleted %s flows which groups were desaggregated by ratio" % cursor.rowcount

    cursor.execute(
        """SELECT count(distinct partner) FROM flow_aggregated where partner_type = 'group'""")
    print "now flow_aggregated counts %s partner groups " % cursor.fetchone()
    cursor.execute(
        """SELECT count(*) FROM flow_aggregated where partner_type = 'group'""")
    print "now flow_aggregated counts %s flows with partner groups " % cursor.fetchone()
