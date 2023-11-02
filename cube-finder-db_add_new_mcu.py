import argparse
import os
import logging
import json

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import declarative_base, sessionmaker

from rpn import Rpn
from cpn import Cpn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def copy_database(path, out_path):
    """
    将Sqlite数据库复制到新的路径
    :param path:
    :param out_path:
    :return:
    """
    if os.path.exists(out_path):
        os.remove(out_path)
    with open(path, 'rb') as f:
        data = f.read()
    with open(out_path, 'wb') as f:
        f.write(data)
    logging.info('Copy database from {} to {} success!'.format(path, out_path))


def main():
    parser = argparse.ArgumentParser(description='Add new MCU to the cube-finder-db')
    parser.add_argument('--path', metavar='-p', type=str, help='Path to database')
    parser.add_argument('--out', metavar='-o', type=str, help='Output path')

    args = parser.parse_args()
    copy_database(args.path, args.out)

    engine = create_engine('sqlite:///' + args.out)
    Base = automap_base()
    Base.prepare(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    base_dir = './MCU'
    for family in os.listdir(base_dir):
        _dir = os.path.join(base_dir, family)
        if os.path.isdir(_dir):
            for subFamily in os.listdir(_dir):
                _sub_dir = os.path.join(_dir, subFamily)
                if os.path.isdir(_sub_dir):
                    for rpn in os.listdir(_sub_dir):
                        _rpn_dir = os.path.join(_sub_dir, rpn)
                        if os.path.isdir(_rpn_dir):
                            _rpn = Rpn(session, Base, _rpn_dir)
                            _rpn.add()
                            _cpn = Cpn(session, Base, _rpn_dir, _rpn.get_id())
                            _cpn.add()
                            logging.info('Add {} to database'.format(rpn))
                        else:
                            logging.warning('Not a directory: {}'.format(_rpn_dir))


if __name__ == '__main__':
    main()
