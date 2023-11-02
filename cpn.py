import json
import logging

from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base
from rpn import Rpn, SqlBase

class RpnHasCpn(SqlBase):
    __tablename__ = 'rpn_has_cpn'
    rpn_id = Column(Integer, primary_key=True)
    cpn_id = Column(Integer, primary_key=True)


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

            self.add_attribute(item['attribute'], cpn_id)
            self.add_rpn_has_cpn(cpn_id)

    def get_attribute_id(self, name: str):
        """
        获取属性的ID
        :return:
        """
        attribute = self.database.classes.attribute
        id = self.session.query(attribute).filter(attribute.name == name).first().id
        return id

    def add_attribute(self, attribute: list, cpn_id: str):
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
