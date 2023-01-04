import pandas as pd

from db_helper import db_connection_open, is_user_email_in_db, is_tag_in_db


def parse_file(link, filetype):
    """
    
    @param link:
    @param filetype:
    @return:
    """
    if filetype == 'xlsx':
        xd = pd.ExcelFile(link)
        df = xd.parse(xd.sheet_names[0], index_col=0, comment='#')
    else:
        df = pd.read_csv(link)
    emails_list_ = df['email'].tolist()
    groups_list_ = df['group'].tolist()
    users_tags_df = df[["emails", "groups"]]

    my_db = db_connection_open()
    my_cursor = my_db.cursor()
    for email_ in emails_list_:
        if not is_user_email_in_db(my_cursor, email_):
            my_cursor.execute(
                "insert into users (user_email, is_present) value ('{u_email}', false);".format(u_email=email_))
    for tag_name_ in groups_list_:
        if not is_tag_in_db(my_cursor, tag_name_):
            my_cursor.execute("insert into tags (tag_name) value ('{tag_n}');".format(tag_n=tag_name_))

    for i in range(len(users_tags_df)):
        user_email_ = users_tags_df.loc[i, "emails"]
        user_tag_ = users_tags_df.loc[i, "groups"]
        my_cursor.execute("select user_id from users where user_email like '{u_email}'".format(u_email=user_email_))
        user_id_ = my_cursor.fetchone()[0]
        my_cursor.execute("select tag_id from tags where tag_name like '{tag_n}'".format(tag_n=user_tag_))
        tag_id_ = my_cursor.fetchone()[0]
        my_cursor.execute(
            "insert into users_tags (user_id, tag_id) value ('{u_id}', '{t_id}')".format(u_id=user_id_, t_id=tag_id_))

    my_db.commit()
    my_cursor.close()
    my_db.close()
    return emails_list_, groups_list_
