import json
import logging

from sqlalchemy import Column, Integer, VARBINARY
from sqlalchemy.orm import declarative_base

SqlBase = declarative_base()


class Feature(SqlBase):
    __tablename__ = 'feature'
    id = Column(Integer, primary_key=True)
    name = Column(VARBINARY(1024))


class FeatureItem(SqlBase):
    __tablename__ = 'featureitem'
    id = Column(Integer, primary_key=True)
    item = Column(VARBINARY(1024))


class Rpn(object):
    def __init__(self, session, database, rpn_path: str):
        self.session = session
        self.database = database
        self.rpn_path = rpn_path
        self.data = {}
        with open(rpn_path + '/rpn.json', 'r', encoding='utf-8') as f:
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
        with open(self.rpn_path + '/attribute.json', 'r', encoding='utf-8') as f:
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

    def get_feature_id(self, name: str) -> int:
        """
        获取特性的ID
        :param name:
        :return:
        """
        feature = Feature
        name = name.encode('utf-8')

        feature_id_count = self.session.query(feature).filter(feature.name == name).count()
        if feature_id_count == 0:
            return self.session.query(feature).all()[-1].id + 1
        else:
            return self.session.query(feature).filter(feature.name == name).first().id

    def get_feature_item_id(self, name: str) -> int:
        """
        获取特性项的ID
        :param name:
        :return:
        """
        feature_item = FeatureItem
        name = name.encode('gbk')
        feature_item_id_count = self.session.query(feature_item).filter(feature_item.item == name).count()
        if feature_item_id_count == 0:
            return self.session.query(feature_item).all()[-1].id + 1
        else:
            return self.session.query(feature_item).filter(feature_item.item == name).first().id

    def add_feature(self):
        """
        添加特性
        :return:
        """
        rpn_feature = self.database.classes.rpn_has_featurelist
        with open(self.rpn_path + '/featurelist.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for feature in data:
            feature_name = feature['name']
            feature_id = self.get_feature_id(feature_name)
            feature_rank = feature['rank']

            for item in feature['item']:
                feature_item_name = item['name']
                feature_item_id = self.get_feature_item_id(feature_item_name)
                feature_item_rank = item['rank']
                new_rpn_feature = rpn_feature(
                    rpn_id=self.get_id(),
                    feature_id=feature_id,
                    feature_rank=feature_rank,
                    featureItem_id=feature_item_id,
                    item_rank=feature_item_rank
                )
                self.session.add(new_rpn_feature)
                self.session.commit()

    def add(self):
        self.add_rpn()
        self.add_attribute()
        self.add_feature()
