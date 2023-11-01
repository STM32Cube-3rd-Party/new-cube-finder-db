import argparse
import os
import logging
import json

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SqlBase = declarative_base()


class RpnHasCpn(SqlBase):
    __tablename__ = 'rpn_has_cpn'
    rpn_id = Column(Integer, primary_key=True)
    cpn_id = Column(Integer, primary_key=True)


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


class Rpn(object):
    def __init__(self, session, database, rpn_path: str):
        self.session = session
        self.database = database
        self.rpn_path = rpn_path
        self.data = {}
        with open(rpn_path + '/rpn.json', 'r') as f:
            self.data = json.load(f)

    def get_id(self):
        """
        获取RPN的ID
        :return:
        """
        rpn = self.database.classes.rpn
        if self.check() == False:
            return self.session.query(rpn).all()[-1].id + 1
        else:
            return self.session.query(rpn).filter(rpn.rpn == self.data['rpn_name']).first().id

    def check(self) -> bool:
        """
        检查RPN是否存在
        :return:
        """
        rpn = self.database.classes.rpn
        rpn_id_count = self.session.query(rpn).filter(rpn.rpn == self.data['rpn_name']).count()
        if rpn_id_count == 0:
            return False
        else:
            return True

    def add_rpn(self):
        """
        添加RPN
        :param session:
        :param rpn_path:
        :return:
        """
        if self.check():
            logging.warning('RPN {} already exists!'.format(self.data['rpn_name']))
            return
        rpn_id = self.get_id()
        rpn = self.database.classes.rpn
        new_rpn = rpn(
            id=rpn_id,
            rpn=self.data['rpn_name'],
            class_id='1734',
            published='1',
            publishingState='Activate',
            marketingStatus='Active',
            marketingRestriction='Public',
            description=self.data['description'],
            longDescription=self.data['longDescription'],
            # circuitDiagramURL=self.data['circuitDiagramUrl'],
            path=self.data['path'],
            imageURL=self.data['imageURL'],
        )
        self.session.add(new_rpn)
        self.session.commit()

    def get_attribute_id(self, name: str) -> int:
        """
        获取属性的ID
        :param name:
        :return:
        """
        attribute = self.database.classes.attribute
        attribute_id_count = self.session.query(attribute).filter(attribute.name == name).count()
        if attribute_id_count == 0:
            return self.session.query(attribute).last().id + 1
        else:
            return self.session.query(attribute).filter(attribute.name == name).first().id

    def add_attribute(self):
        """
        添加属性
        :return:
        """
        rpn_attribute = self.database.classes.rpn_has_attribute
        with open(self.rpn_path + '/attribute.json', 'r') as f:
            data = json.load(f)

        for item in data:
            attribute_id = self.get_attribute_id(item['name'])
            new_rpn_attribute = rpn_attribute(
                rpn_id=self.get_id(),
                attribute_id=attribute_id,
                strValue=item['strValue'],
                numValue=item['numValue']
            )
            self.session.add(new_rpn_attribute)
            self.session.commit()

    def add(self):
        self.add_rpn()
        self.add_attribute()


class Cpn(object):
    def __init__(self, session, database, cpn_path: str, rpn_id: int):
        self.session = session
        self.database = database
        self.cpn_path = cpn_path
        self.rpn_id = rpn_id
        self.cpn_id = {}
        self.data = []
        with open(cpn_path + '/cpn.json', 'r') as f:
            self.data = json.load(f)

    def check(self, name: str) -> bool:
        """
        检查CPN是否存在
        :return:
        """
        cpn = self.database.classes.cpn
        cpn_id_count = self.session.query(cpn).filter(cpn.cpn == name).count()
        if cpn_id_count == 0:
            return False
        else:
            return True

    def get_id(self, name):
        """
        获取CPN的ID
        :return:
        """
        cpn = self.database.classes.cpn
        if self.check(name) == False:
            return self.session.query(cpn).all()[-1].id + 1
        else:
            return self.session.query(cpn).filter(cpn.name == name).first().id

    def add_cpn(self):
        """
        添加CPN
        :param session:
        :param cpn_path:
        :return:
        """
        cpn = self.database.classes.cpn
        for item in self.data:
            if self.check(item['cpn_name']):
                logging.warning('CPN {} already exists!'.format(item['name']))
                continue
            cpn_id = self.get_id(item['cpn_name'])
            new_cpn = cpn(
                id=cpn_id,
                cpn='STM32' + item['cpn_name'],
                refname=item['refname'],
                prmis_id='114514'
            )
            self.session.add(new_cpn)
            self.session.commit()

            self.add_attrbute(item['attribute'], cpn_id)
            self.add_rpn_has_cpn(cpn_id)

    def get_attribute_id(self, name: str):
        """
        获取属性的ID
        :return:
        """
        attribute = self.database.classes.attribute
        id = self.session.query(attribute).filter(attribute.name == name).first().id
        return id

    def add_attrbute(self, attribute: list, cpn_id: str):
        """
        添加属性
        :return:
        """
        cpn_attribute = self.database.classes.cpn_has_attribute
        for item in attribute:
            attribute_id = self.get_attribute_id(item['name'])
            new_attribute = cpn_attribute(
                cpn_id=cpn_id,
                attribute_id=attribute_id,
                strValue=item['strValue'],
                numValue=item['numValue']
            )
            self.session.add(new_attribute)
            self.session.commit()

    def add_rpn_has_cpn(self, cpn_id: int):
        """
        添加RPN和CPN的关系
        :return:
        """
        new_rpn_has_cpn = RpnHasCpn(
            rpn_id=self.rpn_id,
            cpn_id=cpn_id
        )
        self.session.add(new_rpn_has_cpn)
        self.session.commit()

    def add(self):
        return self.add_cpn()


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
