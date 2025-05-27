import uuid

import os
from flask import render_template, request, flash, redirect, session
from flask_login import login_user, logout_user, current_user
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask_apscheduler import APScheduler
from sqlalchemy.orm import aliased

from app import app
from forms import LoginForm, RegistrationForm
from models import User, db, Product, Order, OrderItem, OrderProblem, Transaction

faq_data = [
    {"question": "Can I request a delivery time slot that corresponds to a specific mealtime?", "label": "delivery"},
    {"question": "Is there a membership program?", "label": "membership"},
    {"question": "What is the script for obtaining a proof of purchase, and can you provide an img?", "label": "order"},
    {"question": "What payment methods do you accept, img of accepted card logos?", "label": "payment"},
    {"question": "What are your policies regarding product freshness for perishable items?", "label": "freshness"},
    {"question": "How do I get a receipt for my order?", "label": "order"},
    {"question": "What is your policy on product availability during peak hours?", "label": "availability"},
    {"question": "Is there a way to filter products by dietary restrictions?", "label": "product"},
    {"question": "How can I view the nutritional information for your products?", "label": "nutrition"},
    {"question": "What types of products do you deliver?", "label": "product"},
    {"question": "What is the policy on order cancellations and fees?", "label": "order"},
    {"question": "How can I change my account's mailing address?", "label": "account"},
    {"question": "What is your policy on handling product shortages?", "label": "stock"},
    {"question": "How can I provide suggestions for new product additions to your catalog?", "label": "product"},
    {"question": "What happens if a product I want is temporarily out of stock?", "label": "stock"},
    {"question": "How can I find out about any upcoming holiday promotions or discounts?", "label": "discount"},
    {"question": "How do I report a website issue that's affecting my shopping experience?", "label": "website"},
    {"question": "Can I schedule recurring deliveries for specific items?", "label": "subscription"},
    {"question": "What is your delivery time frame?", "label": "delivery"},
    {"question": "Do you have a customer satisfaction guarantee script?", "label": "satisfaction"},
    {"question": "Do you have a script for price matching?", "label": "pricing"},
    {"question": "Is there a customer review section on the website?", "label": "feedback"},
    {"question": "Do you offer nutritional information for your products?", "label": "nutrition"},
    {"question": "What's your process for managing out-of-stock items?", "label": "stock"},
    {"question": "What is the process for bulk ordering of products?", "label": "order"},
    {"question": "How do I update my account information?", "label": "account"},
    {"question": "Can I change the payment method for an existing order?", "label": "payment"},
    {"question": "What are the options for contacting customer service?", "label": "support"},
    {"question": "What are the terms and conditions for your loyalty program?", "label": "loyalty"},
    {"question": "What do I do if I receive a product that is close to its expiration date?", "label": "product"},
    {"question": "What security measures are in place to protect my data?", "label": "security"},
    {"question": "What is your script for handling customer complaints?", "label": "complaint"},
    {"question": "Can I contact support through social media?", "label": "support"},
    {"question": "What's your policy on handling product requests for customers with allergies?", "label": "allergies"},
    {"question": "How do I initiate a return for an item that doesn't fit my needs?", "label": "return"},
    {"question": "How do I unsubscribe from marketing emails?", "label": "unsubscribe"},
    {"question": "How much does the delivery cost?", "label": "cost"},
    {"question": "Is there an option to add a personalized message to a gift order?", "label": "gift"},
    {"question": "How can I view my order history?", "label": "order"},
    {"question": "What is your process for updating account preferences?", "label": "account"},
    {"question": "Do you offer custom packaging for special occasions?", "label": "packaging"},
    {"question": "What's your policy on handling items returned due to expired shelf life?", "label": "return"},
    {"question": "Do you offer eco-friendly packaging options?", "label": "packaging"},
    {"question": "What happens if my order is lost during delivery?", "label": "delivery"},
    {"question": "How do I check if a product is available in my area?", "label": "availability"},
    {"question": "Can I request a delivery schedule that includes instructions for a secure drop-off location?", "label": "delivery"},
    {"question": "How can I request a copy of my order receipt?", "label": "order"},
    {"question": "What is your policy on handling product complaints?", "label": "complaint"},
    {"question": "What's your process for managing items in a wishlist that are no longer available?", "label": "list"},
    {"question": "How can I report a technical issue with the website script?", "label": "website"},
    {"question": "Is there a time frame for using gift cards?", "label": "gift"},
    {"question": "How do I create a shopping list?", "label": "list"},
    {"question": "What's your policy on handling product recalls from suppliers?", "label": "recall"},
    {"question": "What should I do if I receive a damaged product?", "label": "return"},
    {"question": "What's the process for reordering items from my order history?", "label": "order"},
    {"question": "How do I apply a coupon code?", "label": "discount"},
    {"question": "Can I change the delivery address for an order that's already in transit?", "label": "delivery"},
    {"question": "What happens if I'm not at home when my order arrives?", "label": "delivery"},
    {"question": "How can I leave feedback or a review?", "label": "feedback"},
    {"question": "Do you have a press kit available that includes company logos and release templates?", "label": "media"},
    {"question": "How do I manage my subscription preferences?", "label": "subscription"},
    {"question": "What is the average delivery time?", "label": "delivery"},
    {"question": "How do I apply a promotional code to my order?", "label": "discount"},
    {"question": "Is there a policy for recycling product packaging materials?", "label": "environment"},
    {"question": "How do I get notified of product restocks?", "label": "notification"},
    {"question": "Do you have a blog with product updates?", "label": "blog"},
    {"question": "Is there a referral program for inviting friends to your service?", "label": "referral"},
    {"question": "What is the script for product recalls?", "label": "recall"},
    {"question": "What is the process for requesting a refund?", "label": "refund"},
    {"question": "What do I do if I receive a product with a short shelf life?", "label": "product"},
    {"question": "Can I request a delivery time slot that ensures products are delivered at their peak freshness?", "label": "freshness"},
    {"question": "What happens if an item is out of stock?", "label": "stock"},
    {"question": "How can I apply for a job at your company?", "label": "career"},
    {"question": "How can I provide feedback on the delivery experience?", "label": "feedback"},
    {"question": "Is there a script for addressing customer complaints about delivery delays?", "label": "complaint"},
    {"question": "What's your policy on handling products that arrive damaged during extreme weather conditions?", "label": "environment"},
    {"question": "What is your policy on bulk orders?", "label": "order"},
    {"question": "What should I do if a product I received as a gift needs to be returned?", "label": "return"},
    {"question": "Is there a minimum order amount?", "label": "order"},
    {"question": "Is there a limit to the number of items I can add to my wishlist?", "label": "list"},
    {"question": "Are there any restrictions on delivery time slots?", "label": "delivery"},
    {"question": "Do you have a mobile app for iOS devices?", "label": "app"},
    {"question": "How do I know if a product is in stock?", "label": "stock"},
    {"question": "Is there a process for consolidating multiple loyalty cards into one account?", "label": "loyalty"},
    {"question": "Is there a mobile app available for Android users?", "label": "app"},
    {"question": "What's your process for managing and disposing of packaging waste?", "label": "environment"},
    {"question": "What is the expiration date policy for products?", "label": "product"},
    {"question": "How do I check if a product is available for international delivery?", "label": "delivery"},
    {"question": "What do I do if I receive a promotional code?", "label": "discount"},
    {"question": "What are the options for contacting your technical support team?", "label": "support"},
    {"question": "How can I track my order?", "label": "order"},
    {"question": "Do you offer a subscription service?", "label": "subscription"},
    {"question": "How do I manage my delivery preferences for specific items?", "label": "delivery"},
    {"question": "What is your policy on price adjustments?", "label": "pricing"},
    {"question": "What do I do if my order is damaged and have an img? Where to send the img?", "label": "return"},
    {"question": "How can I find product reviews from other customers?", "label": "feedback"},
    {"question": "Can I apply for a job through your mobile app?", "label": "career"},
    {"question": "What should I do if I receive the wrong item?", "label": "order"},
    {"question": "Is there a process for replacing damaged loyalty cards?", "label": "loyalty"},
    {"question": "How can I receive updates on your latest products and offers?", "label": "newsletter"},
    {"question": "What steps should I take if I'm having trouble placing an order?", "label": "order"},
    {"question": "How do I add or remove items from my order after checkout?", "label": "order"},
    {"question": "How are orders packaged to ensure product freshness during transport?", "label": "packaging"},
    {"question": "How do I redeem my loyalty card points for discounts?", "label": "loyalty"},
    {"question": "What happens if my order is delayed?", "label": "delivery"},
    {"question": "Can I request a delivery time slot specifically for business hours?", "label": "delivery"},
    {"question": "What is the product quality guarantee?", "label": "quality"},
    {"question": "Can I purchase gift cards in physical stores?", "label": "gift"},
    {"question": "How do I apply a store credit to my order?", "label": "payment"},
    {"question": "Can I use a combination of payment methods for a single order?", "label": "payment"},
    {"question": "Can I change the payment method for an order?", "label": "payment"},
    {"question": "Are there any special promotions or discounts for first-time customers?", "label": "discount"},
    {"question": "What types of packaging do you offer for fragile items?", "label": "packaging"},
    {"question": "How can I change the delivery address for my loyalty card?", "label": "loyalty"},
    {"question": "How do I report a technical issue on the mobile app?", "label": "app"},
    {"question": "What is the product expiration date policy?", "label": "product"},
    {"question": "How can I provide feedback about the condition of delivered products?", "label": "feedback"},
    {"question": "What do I do if I didn't receive an order confirmation email?", "label": "email"},
    {"question": "What is the process for bulk ordering?", "label": "order"},
    {"question": "What happens if I receive a product that doesn't match the description on your website?", "label": "product"},
    {"question": "How can I ensure the accuracy of my delivery address?", "label": "delivery"},
    {"question": "How can I contact customer support?", "label": "support"},
    {"question": "Can I specify delivery instructions as a script to the courier?", "label": "delivery"},
    {"question": "What are the terms and conditions for your referral program?", "label": "referral"},
    {"question": "How do I track my order status?", "label": "order"},
    {"question": "What happens if I have allergies to certain ingredients?", "label": "allergies"},
    {"question": "Can I cancel an order after it's been placed?", "label": "order"},
    {"question": "Is there a policy for handling products that arrive damaged due to environmental factors?", "label": "environment"},
    {"question": "Are there any discounts available?", "label": "discount"},
    {"question": "What areas do you serve?", "label": "delivery"},
    {"question": "Is there a process for addressing issues with delayed order notifications?", "label": "notification"},
    {"question": "Can I request a delivery time slot during non-peak hours?", "label": "delivery"},
    {"question": "How do I report unauthorized activity on my account?", "label": "security"},
    {"question": "What's the process for getting a replacement for a product with a manufacturer defect?", "label": "warranty"},
    {"question": "Is there a warranty for the products you offer?", "label": "warranty"},
    {"question": "What is the policy on product freshness?", "label": "freshness"},
    {"question": "How do I provide feedback on the packaging of products?", "label": "feedback"},
    {"question": "How can I sign up for updates on product recalls?", "label": "recall"},
    {"question": "What is your contact number?", "label": "contact"},
    {"question": "How long does it take to process a refund?", "label": "refund"},
    {"question": "Is there a limit to the number of loyalty cards I can have?", "label": "loyalty"},
    {"question": "Do you offer expedited delivery options?", "label": "delivery"},
    {"question": "How do I sign up for a notification about upcoming product restocks?", "label": "stock"},
    {"question": "What do I do if I forgot my account password?", "label": "password"},
    {"question": "What is your product packaging material made of?", "label": "packaging"},
    {"question": "Can I track my delivery in real-time?", "label": "delivery"},
    {"question": "Do you have a mobile app?", "label": "app"},
    {"question": "Do you offer contactless delivery?", "label": "delivery"},
    {"question": "Is there a limit on the number of items I can order?", "label": "order"},
    {"question": "Can I return a product if I change my mind?", "label": "return"},
    {"question": "Can I place an order over the phone?", "label": "order"},
    {"question": "Do you offer gift cards?", "label": "gift"},
    {"question": "What do I do if I accidentally unsubscribed from your newsletter?", "label": "newsletter"},
    {"question": "Can I change my delivery address after placing an order?", "label": "order"},
    {"question": "Do you provide a product comparison feature on your website?", "label": "product"},
    {"question": "Can I place a bulk order with a mix of different products?", "label": "order"},
    {"question": "What's your policy on eco-friendly and sustainable product options?", "label": "environment"},
    {"question": "What is the product quality inspection process?", "label": "quality"},
    {"question": "Is there a dedicated customer support hotline for loyalty card members?", "label": "loyalty"},
    {"question": "Can I schedule a delivery for a specific date and time?", "label": "delivery"},
    {"question": "How do I apply for a return for a product that doesn't meet the specified product description?", "label": "return"},
    {"question": "What is the process for changing my delivery address?", "label": "delivery"},
    {"question": "How can I make changes to my recurring subscription?", "label": "subscription"},
    {"question": "Can I specify a delivery time frame for my order?", "label": "delivery"},
    {"question": "Do you deliver on weekends?", "label": "delivery"},
    {"question": "What can I do if I'm charged the wrong amount for my order?", "label": "payment"},
    {"question": "What types of notifications do you send to customers?", "label": "notification"},
    {"question": "How do I sign up for a notification about upcoming product releases?", "label": "newsletter"},
    {"question": "What is the minimum order value for free delivery?", "label": "delivery"},
    {"question": "What is your pricing policy?", "label": "pricing"},
    {"question": "What is the script to sign up for a loyalty card?", "label": "loyalty"},
    {"question": "What types of packaging materials do you use?", "label": "packaging"},
    {"question": "What are the delivery hours?", "label": "delivery"},
    {"question": "Is there a live chat support option?", "label": "support"},
    {"question": "Do you have a loyalty card program?", "label": "loyalty"},
    {"question": "How do I subscribe to your newsletter?", "label": "newsletter"},
    {"question": "How are refunds processed?", "label": "return"},
    {"question": "What are the terms and conditions for using store credit?", "label": "payment"},
    {"question": "Is there a loyalty program?", "label": "membership"},
    {"question": "Can I request a specific delivery window for a large event order?", "label": "delivery"},
    {"question": "What is your product return process?", "label": "return"},
    {"question": "How do I redeem a discount code shared on your social media channels?", "label": "discount"},
    {"question": "Is there a limit to the distance for delivery locations?", "label": "delivery"},
    {"question": "Do you offer additional services like product assembly or installation?", "label": "service"},
    {"question": "Can I request a refund if my order is damaged during delivery?", "label": "refund"},
    {"question": "How can I join your loyalty program?", "label": "loyalty"},
    {"question": "Are there any restrictions on delivery addresses?", "label": "delivery"},
    {"question": "How are orders packaged to keep them fresh?", "label": "packaging"},
    {"question": "How can I inquire about job openings at your company?", "label": "career"},
    {"question": "Do you offer expedited delivery options for last-minute orders?", "label": "delivery"},
    {"question": "What is the return policy?", "label": "return"},
    {"question": "Is there a way to request a delivery time slot that includes a tracking link?", "label": "delivery"},
    {"question": "Is there a way to request a product not currently available on your website?", "label": "product"},
    {"question": "How do I provide feedback on the mobile app user experience?", "label": "app"},
    {"question": "What is your product?", "label": "product"},
    {"question": "Can I change my account's email address?", "label": "account"},
    {"question": "How can I sign up to receive notifications about your company's career opportunities?", "label": "career"},
    {"question": "How do I create an account?", "label": "account"},
    {"question": "How do I place an order?", "label": "order"},
    {"question": "Can I request a customized delivery schedule for a subscription order?", "label": "subscription"},
    {"question": "Can I place an order from outside your service area?", "label": "delivery"},
    {"question": "What do I do if I forgot my account username?", "label": "account"},
    {"question": "Can I request a specific delivery date and time for a gift order?", "label": "gift"},
    {"question": "How do I find products that are currently on sale?", "label": "pricing"},
    {"question": "How long does it take to process an order?", "label": "order"},
    {"question": "Do you offer weekend delivery options?", "label": "delivery"},
    {"question": "Can I return a product if it's opened?", "label": "return"},
    {"question": "How do I update my loyalty card information?", "label": "loyalty"},
    {"question": "What do I do if I receive an incorrect order?", "label": "order"},
    {"question": "Is there a policy for addressing products that arrive damaged due to mishandling during shipping?", "label": "delivery"},
    {"question": "What is your process for handling product recalls?", "label": "recall"},
    {"question": "Do you offer a satisfaction guarantee on your products?", "label": "satisfaction"},
    {"question": "What happens if a product I ordered is part of a recall?", "label": "recall"},
    {"question": "What's the process for extending the delivery window for large orders?", "label": "delivery"},
    {"question": "What's your policy on handling returned gift items?", "label": "return"},
    {"question": "Is there a referral program for customers?", "label": "referral"},
    {"question": "How can I browse products on your website?", "label": "product"},
    {"question": "What should I do if I experience a technical issue on the website?", "label": "website"},
    {"question": "How can I check the status of my order?", "label": "order"},
    {"question": "How can I get in touch with your PR department for collaboration?", "label": "media"},
    {"question": "What do I do if my delivery doesn't arrive within the specified time frame?", "label": "delivery"},
    {"question": "How do I change my email address in my account?", "label": "account"},
    {"question": "What's the process for returning a product that doesn't meet my expectations?", "label": "return"},
    {"question": "What happens if I have technical issues with the mobile app?", "label": "app"},
    {"question": "Are there any restrictions on product quantity per order?", "label": "order"},
    {"question": "What should I do if I accidentally placed a duplicate order?", "label": "order"},
    {"question": "How do I reset my password?", "label": "password"},
    {"question": "What's the difference between standard and express delivery?", "label": "delivery"},
    {"question": "How do I initiate a return for an item I no longer want?", "label": "return"},
    {"question": "Can I change the delivery date for my order?", "label": "delivery"},
    {"question": "Do you offer expedited shipping for gift cards?", "label": "gift"},
    {"question": "How do I report a security issue or data breach?", "label": "security"},
    {"question": "Is there an option to track the delivery driver's location?", "label": "delivery"},
    {"question": "What should I do if I'm not satisfied with my order?", "label": "complaint"},
    {"question": "What is the process for returning a non-food product?", "label": "return"},
    {"question": "Can I purchase a gift card online?", "label": "gift"},
    {"question": "What is your procedure for handling incorrect pricing on the website?", "label": "pricing"},
    {"question": "Do you offer same-day delivery?", "label": "delivery"},
    {"question": "Can I place an order for delivery to a different address?", "label": "delivery"},
]

tfidf_vectorizer = TfidfVectorizer()
faq_questions = [item['question'] for item in faq_data]
tfidf_matrix = tfidf_vectorizer.fit_transform(faq_questions)


@app.route("/", methods=["GET", "POST"])
def handler():
    context = {}
    template = 'login.html'
    action = request.args.get('action')

    if current_user.is_authenticated:
        match action:
            case 'logout':
                logout_user()
                flash('Logged out successfully.')
                return redirect("/")
            case 'products':
                context['products'] = Product.query.all()
                template = 'products.html'
            case 'add-to-cart':
                product_id = int(request.form.get("productId"))
                quantity = int(request.form.get("quantity"))
                if quantity <= 0:
                    flash('Invalid quantity', 'danger')
                product = Product.query.get(product_id)
                if product:
                    cart = session.get("cart", {})
                    product_key = str(product.id)
                    if cart.get(product_key):
                        cart[product_key] += quantity
                    else:
                        cart[product_key] = quantity
                    session["cart"] = cart
                flash('Product successfully added to the cart.', 'success')
                return redirect('/?action=products')
            case 'cart':
                cart = session.get("cart", {})
                if len(cart) <= 0:
                    flash('Cart is empty', 'danger')
                    return redirect('/?action=products')
                products_in_cart = []
                for product_id, quantity in cart.items():
                    product = Product.query.get(int(product_id))
                    if product:
                        products_in_cart.append({"product": product, "quantity": quantity})
                context['products_in_cart'] = products_in_cart
                template = 'cart.html'
            case 'checkout':
                template = 'order.html'
                order_id = request.args.get('uuid')
                address = request.form.get('address')
                phone = request.form.get('phone')
                email = request.form.get('email')
                if address:
                    session["address"] = address
                if phone:
                    session["phone"] = phone
                if email:
                    session["email"] = email
                cart = session.get("cart", {})
                if order_id:
                    order = Order.query.filter_by(uuid=order_id).first()
                    order_items = order.items.all()
                    context['order_items'] = order_items
                else:
                    total_price = 0
                    order_uuid = str(uuid.uuid4())
                    order = Order(user_id=current_user.id, total_price=total_price, uuid=order_uuid, phone=phone,
                                  email=email, address=address)
                    db.session.add(order)
                    db.session.commit()
                    for product_id, quantity in cart.items():
                        product = Product.query.get(int(product_id))
                        if product:
                            total_price += product.price * quantity
                            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=quantity)
                            db.session.add(order_item)
                    order.total_price = total_price
                    db.session.add(order)
                    db.session.commit()
                    session.pop("cart", None)
                    return redirect(f'/?action=checkout&uuid={order.uuid}')
                context['order'] = order
            case 'clear-cart':
                session.pop("cart", None)
                return redirect('/?action=products')
            case 'order-problem':
                template = 'report_order_problem.html'
                if request.method == 'POST':
                    order_id = request.args.get('uuid')
                    if order_id:
                        order = Order.query.filter_by(uuid=order_id).first()
                        if order.user_id == current_user.id:
                            message = request.form.get('message')
                            if message:
                                order_problem = OrderProblem(order.id, current_user.id, message)
                                db.session.add(order_problem)
                                db.session.commit()
                                flash('Thank you! A manager will contact you as soon as possible', 'success')
                            else:
                                flash('It is not your order', 'danger')
                        else:
                            flash('Order not found', 'danger')
                    else:
                        flash('Order not found', 'danger')
                    return redirect(f'/?action=checkout&uuid={order_id}')
            case 'order-problems':
                if current_user.is_manager:
                    problems = OrderProblem.query.filter_by(resolved=False)
                    context['problems'] = problems
                    template = 'manager/problems_list.html'
            case 'view-problem':
                if current_user.is_manager:
                    problem_id = request.args.get('id')
                    if problem_id:
                        problem = OrderProblem.query.filter_by(id=problem_id).first()
                        if problem:
                            order = Order.query.filter_by(id=problem.order_id).first()
                            if order:
                                order_items = order.items.all()
                                context['order'] = order
                                context['order_items'] = order_items
                                context['problem'] = problem
                                template = 'manager/problem_details.html'
                            else:
                                flash('Order attached to the problem not found', 'danger')
                                return redirect('/?action=order-problems')
                        else:
                            flash('Problem not found', 'danger')
                            return redirect('/?action=order-problems')
                    else:
                        flash('Problem id not found', 'danger')
                        return redirect('/?action=order-problems')
            case 'resolve-problem':
                if current_user.is_manager:
                    problem_id = request.args.get('id')
                    if problem_id:
                        problem = OrderProblem.query.filter_by(id=problem_id).first()
                        if problem:
                            problem.resolved = True
                            db.session.commit()
                            flash('Problem resolved!', 'success')
                        else:
                            flash('Problem not found', 'danger')
                    else:
                        flash('Problem id not found', 'danger')
                    return redirect('/?action=order-problems')
            case 'faq':
                question = request.args.get('question')
                if question:
                    user_question_tfidf = tfidf_vectorizer.transform([question])
                    cosine_similarities = linear_kernel(user_question_tfidf, tfidf_matrix).flatten()
                    most_similar_index = cosine_similarities.argsort()[-1]
                    label = faq_data[most_similar_index]['label']
                    listdir = sorted(os.listdir('templates/faq/answers'))
                    for file in listdir:
                        if label in file:
                            template = '/faq/answers/' + file
                            context['question'] = question
                            break
                    else:
                        flash('Answer not found, please contact us', 'danger')
                        template = 'faq/faq.html'
                else:
                    template = 'faq/faq.html'
            case 'transactions-list':
                sender_user = aliased(User, name='sender_user')
                recipient_user = aliased(User, name='recipient_user')
                transactions = db.session.query(Transaction, sender_user.username.label('sender_username'),
                                                recipient_user.username.label('recipient_username')).join(
                    sender_user, Transaction.sender_id == sender_user.id).join(
                    recipient_user, Transaction.recipient_id == recipient_user.id).filter(
                    (Transaction.sender_id == current_user.id) | (Transaction.recipient_id == current_user.id)
                ).all()
                context['transactions'] = transactions
                template = 'transaction_list.html'
            case 'create-transaction':
                sender = current_user.id
                recipient_name = request.form.get('recipient')
                if recipient_name:
                    if recipient_name != current_user.username:
                        recipient = User.query.filter_by(username=recipient_name).first()
                        if recipient:
                            amount = int(request.form.get('amount'))
                            if amount > 0:
                                form_data = dict(request.form)
                                form_data['amount'] = amount
                                del form_data['recipient']
                                form_data['recipient_id'] = recipient.id
                                transaction = Transaction.update_or_create(current_user.id, form_data)
                                if transaction:
                                    flash('Transaction has been successfully created and will be processed shortly',
                                          'success')
                            else:
                                flash('Invalid amount', 'danger')
                        else:
                            flash('Recipient not found', 'danger')
                    else:
                        flash('You can\'t send points to yourself', 'danger')
                else:
                    flash('Enter a recipient name', 'danger')
                return redirect('/?action=transactions-list')
            case 'delete-account-and-get-flag':
                if current_user.balance >= 999_999_999 and not current_user.is_manager and not current_user.is_admin:
                    current_user.remove()
                    db.session.commit()
                    flash('midnight{********REDACTED********}', 'success')
                return redirect('/')
            case _:
                if current_user.balance >= 999_999_999 and not current_user.is_manager and not current_user.is_admin:
                    context['show_flag_button'] = True
                template = "authenticated_template.html"
    else:
        form = LoginForm()
        context['form'] = form

        if request.method == 'POST':
            if action is None:
                form = LoginForm()
                if form.validate_on_submit():
                    username = form.username.data
                    password = form.password.data
                    user = User.query.filter_by(username=username, password=password).first()
                    if user:
                        login_user(user)
                        return redirect('/')
                    flash('Invalid username or password', 'danger')
            elif action == 'registration':
                form = RegistrationForm()
                if form.validate_on_submit():
                    username = form.username.data
                    password = form.password.data
                    user = User.query.filter_by(username=username).first()
                    if not user:
                        new_user = User(username=username, password=password)
                        db.session.add(new_user)
                        db.session.commit()
                        flash('Registered successfully', 'success')
                        return redirect('/')
                    flash('User exists', 'danger')
                    return redirect('/?action=registration')

        match action:
            case 'registration':
                form = RegistrationForm()
                context['form'] = form
                template = "register.html"

    return render_template(template, context=context)

scheduler = APScheduler()

def confirm_transaction():
    with app.app_context():
        pending_transactions = Transaction.query.filter(Transaction.status == 'pending').all()
        for transaction in pending_transactions:
            if transaction.amount <= 10:
                transaction.status = 'confirmed'
            else:
                transaction.status = 'pending-manual-check'
        db.session.commit()

scheduler.add_job(id='confirm_transaction', func=confirm_transaction, trigger="interval", seconds=0.1)

def send_transaction():
    with app.app_context():
        confirmed_transactions = Transaction.query.filter(Transaction.status == 'confirmed').all()

        for transaction in confirmed_transactions:
            sender = User.query.get(transaction.sender_id)
            recipient = User.query.get(transaction.recipient_id)
            if sender and recipient:
                if sender.balance >= transaction.amount:
                    transaction.status = 'sent'
                    if not sender.is_manager:
                        sender.balance -= transaction.amount
                    recipient.balance += transaction.amount
                else:
                    transaction.status = 'rejected'
        db.session.commit()

scheduler.add_job(id='send_transaction', func=send_transaction, trigger="interval", seconds=0.13)

scheduler.start()
