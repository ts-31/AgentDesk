from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from models import Subscription
from schemas import SubscriptionBase, SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("", response_model=List[SubscriptionResponse])
def get_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Subscription).offset(skip).limit(limit).all()


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(subscription_id: UUID, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.subscription_id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub
