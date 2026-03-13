from app.database import SessionLocal
from app import models

def seed():
    db = SessionLocal()
    # Создание зданий
    b1 = models.Building(address="г. Москва, ул. Ленина 1, офис 3", latitude=55.7558, longitude=37.6173)
    b2 = models.Building(address="г. Москва, ул. Тверская 5", latitude=55.7580, longitude=37.6180)
    db.add_all([b1, b2])
    db.commit()

    # Создание деятельностей (дерево)
    food = models.Activity(name="Еда")
    db.add(food)
    db.commit()
    meat = models.Activity(name="Мясная продукция", parent_id=food.id)
    milk = models.Activity(name="Молочная продукция", parent_id=food.id)
    db.add_all([meat, milk])
    db.commit()

    # Организации
    org1 = models.Organization(name="ООО Рога и Копыта", building_id=b1.id)
    org2 = models.Organization(name="Мясной двор", building_id=b2.id)
    db.add_all([org1, org2])
    db.commit()

    # Телефоны
    db.add(models.PhoneNumber(organization_id=org1.id, number="2-222-222"))
    db.add(models.PhoneNumber(organization_id=org1.id, number="8-923-666-13-13"))
    db.add(models.PhoneNumber(organization_id=org2.id, number="3-333-333"))
    db.commit()

    # Связь с деятельностью
    org1.activities.append(food)
    org1.activities.append(meat)
    org2.activities.append(meat)
    db.commit()