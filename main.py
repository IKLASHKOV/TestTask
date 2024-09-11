from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.sql import distinct
from database import Product, ProductCreate, get_db
import uvicorn

app = FastAPI()

@app.post("/products/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, price=product.price, category=product.category)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products/")
def read_products(
        name: str = None,
        min_price: float = None,
        max_price: float = None,
        category: str = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        db: Session = Depends(get_db)
):
    query = db.query(Product)
    if name:
        query = query.filter(Product.name.like(f"%{name}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if category:
        query = query.filter(Product.category == category)

    if sort_order == "asc":
        query = query.order_by(asc(getattr(Product, sort_by)))
    else:
        query = query.order_by(desc(getattr(Product, sort_by)))
    return query.all()


@app.get("/categories/")
def read_categories(db: Session = Depends(get_db)):
    categories = db.query(distinct(Product.category)).all()
    return [category[0] for category in categories]


@app.get("/products/{product_id}")
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}")
def update_product(product_id: int, product_data: ProductCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product.name = product_data.name
    product.price = product_data.price
    product.category = product_data.category
    db.commit()
    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
