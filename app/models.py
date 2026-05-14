# # from sqlalchemy import Column, Integer, Float, DateTime
# # from sqlalchemy.sql import func
# # from .database import Base

# # class SensorReading(Base):
# #     __tablename__ = "sensor_readings"

# #     id = Column(Integer, primary_key=True, index=True)
# #     nitrogen = Column(Float, nullable=False)
# #     phosphorus = Column(Float, nullable=False)
# #     potassium = Column(Float, nullable=False)
# #     ph = Column(Float, nullable=False)
# #     temperature = Column(Float, nullable=False)
# #     humidity = Column(Float, nullable=False)
# #     ec = Column(Float, nullable=False)
# #     timestamp = Column(DateTime(timezone=True), server_default=func.now())


# from sqlalchemy import Column, Integer, Float, DateTime
# from sqlalchemy.sql import func
# from datetime import datetime
# from .database import Base

# class SensorReading(Base):
#     __tablename__ = "sensor_readings"

#     id = Column(Integer, primary_key=True, index=True)
#     nitrogen = Column(Float, nullable=False)
#     phosphorus = Column(Float, nullable=False)
#     potassium = Column(Float, nullable=False)
#     ph = Column(Float, nullable=False)
#     temperature = Column(Float, nullable=False)
#     humidity = Column(Float, nullable=False)
#     ec = Column(Float, nullable=False)
#     timestamp = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)  # ✅ Added default















#from zoneinfo import ZoneInfo

# from sqlalchemy import Column, Integer, Float, DateTime
# from sqlalchemy.sql import func
# from datetime import datetime
# from .database import Base



from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, Float, DateTime
from database import Base

PK_TZ = timezone(timedelta(hours=5))  # UTC+5

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(String, index=True, nullable=False)  # re-enable if you still need per-user scoping
    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    ec = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(PK_TZ))
