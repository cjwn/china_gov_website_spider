from tools import DbBot, solve_mct, solve_nrta


if __name__ == '__main__':
    # get_content(url)
    db = DbBot()
    db.create_table() 
    solve_nrta(db)
    solve_mct(db)
