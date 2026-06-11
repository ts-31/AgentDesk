import random
from faker import Faker
from datetime import timedelta
from database import SessionLocal
from models import Customer, User, Subscription, Invoice, Ticket

fake = Faker()

def seed_database():
    db = SessionLocal()
    
    try:
        print("Starting database seed...")

        # 1. Generate 50 Customers
        print("Seeding 50 Customers...")
        customers = []
        plan_types = ["Free", "Pro", "Business", "Enterprise"]
        for _ in range(50):
            customer = Customer(
                company_name=fake.company(),
                plan_type=random.choice(plan_types),
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            db.add(customer)
            customers.append(customer)
        db.commit()

        # 2. Generate 100 Users
        print("Seeding 100 Users...")
        users = []
        roles = ["Admin", "Member", "Guest"]
        for _ in range(100):
            customer = random.choice(customers)
            user = User(
                customer_id=customer.customer_id,
                email=fake.unique.email(),
                role=random.choice(roles),
                sso_enabled=fake.boolean(chance_of_getting_true=25)
            )
            db.add(user)
            users.append(user)
        db.commit()

        # 3. Generate 50 Subscriptions (1 per customer generally)
        print("Seeding 50 Subscriptions...")
        subscriptions = []
        billing_cycles = ["Monthly", "Annual"]
        statuses = ["Active", "Active", "Active", "Past Due", "Canceled"]
        
        for customer in customers:
            status = random.choice(statuses)
            start_date = fake.date_time_between(start_date='-1y', end_date='now')
            end_date = start_date + timedelta(days=365) if random.choice(billing_cycles) == "Annual" else start_date + timedelta(days=30)
            
            canceled_at = fake.date_time_between(start_date=start_date, end_date='now') if status == "Canceled" else None
            
            subscription = Subscription(
                customer_id=customer.customer_id,
                plan_tier=customer.plan_type, # align tier with the customer's base plan
                billing_cycle=random.choice(billing_cycles),
                status=status,
                start_date=start_date,
                end_date=end_date,
                canceled_at=canceled_at,
                auto_renew=status != "Canceled"
            )
            db.add(subscription)
            subscriptions.append(subscription)
        db.commit()

        # 4. Generate 200 Invoices
        print("Seeding 200 Invoices...")
        invoices = []
        invoice_statuses = ["Paid", "Paid", "Paid", "Unpaid", "Void"]
        for _ in range(200):
            customer = random.choice(customers)
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
            due_date = created_at + timedelta(days=30)
            status = random.choice(invoice_statuses)
            paid_at = created_at + timedelta(days=random.randint(1, 29)) if status == "Paid" else None
            
            invoice = Invoice(
                customer_id=customer.customer_id,
                amount=round(random.uniform(50.0, 5000.0), 2),
                status=status,
                created_at=created_at,
                due_date=due_date,
                paid_at=paid_at,
                billing_period_start=created_at - timedelta(days=30),
                billing_period_end=created_at
            )
            db.add(invoice)
            invoices.append(invoice)
        db.commit()

        # 5. Generate 200 Tickets
        print("Seeding 200 Tickets...")
        tickets = []
        categories = ["Billing", "Login", "SSO", "API", "Workspace", "Permissions"]
        ticket_statuses = ["Open", "In Progress", "Resolved", "Resolved", "Escalated"]
        priorities = ["Low", "Medium", "High", "Urgent"]
        
        for _ in range(200):
            user = random.choice(users)
            ticket = Ticket(
                customer_id=user.customer_id, # Link directly to the user's workspace
                user_id=user.user_id,
                category=random.choice(categories),
                status=random.choice(ticket_statuses),
                priority=random.choice(priorities),
                created_at=fake.date_time_between(start_date='-6m', end_date='now')
            )
            db.add(ticket)
            tickets.append(ticket)
        db.commit()

        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
