from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import User, Product, Transaction, Coupon, AccessCode
import json
from decimal import Decimal

def login_view(request):
    if request.method == 'POST':
        access_code = request.POST.get('access_code')
        if AccessCode.objects.filter(code=access_code).exists():
            request.session['has_access'] = True
            return redirect('index')
        else:
            return render(request, 'polls/login.html', {'error': 'Invalid access code'})
    return render(request, 'polls/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def index(request):
    if not request.session.get('has_access'):
        return redirect('login')
    return render(request, 'polls/index.html')

def users_api(request):
    if request.method == 'GET':
        users = User.objects.all().values()
        return JsonResponse(list(users), safe=False)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                total_spent=0
            )
            return JsonResponse({'id': user.id, 'name': user.name, 'email': user.email, 'phone': user.phone, 'total_spent': user.total_spent})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def user_api(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'total_spent': user.total_spent,
            'points': user.points,
            'history': user.history
        })
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            user.save()
            return JsonResponse({'id': user.id, 'name': user.name, 'email': user.email, 'phone': user.phone, 'total_spent': user.total_spent, 'points': user.points})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)
    elif request.method == 'DELETE':
        user.delete()
        return JsonResponse({'message': 'User deleted successfully'})

def products_api(request):
    if request.method == 'GET':
        products = Product.objects.all().values()
        return JsonResponse(list(products), safe=False)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            product = Product.objects.create(
                name=data['name'],
                price=data['price'],
                description=data['description']
            )
            return JsonResponse({'id': product.id, 'name': product.name, 'price': product.price, 'description': product.description})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def product_api(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'id': product.id, 'name': product.name, 'price': product.price, 'description': product.description})
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            product.name = data.get('name', product.name)
            product.price = data.get('price', product.price)
            product.description = data.get('description', product.description)
            product.save()
            return JsonResponse({'id': product.id, 'name': product.name, 'price': product.price, 'description': product.description})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)
    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse({'message': 'Product deleted successfully'})

def payments_api(request):
    if request.method == 'GET':
        transactions = Transaction.objects.all()
        data = [{
            'id': t.id,
            'userName': t.user.name,
            'products': t.products,
            'quantity': t.quantity,
            'total': t.amount,
            'date': t.timestamp.strftime('%Y-%m-%d')
        } for t in transactions]
        return JsonResponse(data, safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        user = User.objects.get(id=data['userId'])
        products = data['products']
        total = Decimal(data['total'])
        coupon_code = data.get('coupon')
        use_points = data.get('use_points', False)

        discount = Decimal(0)
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                if coupon.is_percentage:
                    discount += total * (coupon.discount / Decimal(100))
                else:
                    discount += coupon.discount
                coupon.active = False
                coupon.save()
            except Coupon.DoesNotExist:
                return JsonResponse({'error': 'Invalid coupon code'}, status=400)

        if use_points:
            discount += Decimal(user.points) / Decimal(100)
            user.points = 0

        total -= discount
        
        transaction = Transaction.objects.create(
            user=user,
            products=products,
            quantity=sum(p['quantity'] for p in products),
            amount=total
        )

        user.total_spent += total
        user.points += int(total * 1) # 1% of the amount
        
        if not isinstance(user.history, list):
            user.history = []
            
        user.history.append({
            'products': products,
            'total': str(total),
            'date': transaction.timestamp.strftime('%Y-%m-%d')
        })
        user.save()

        return JsonResponse({'id': transaction.id})

def payment_api(request, payment_id):
    try:
        transaction = Transaction.objects.get(id=payment_id)
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)

    if request.method == 'DELETE':
        transaction.delete()
        return JsonResponse({'message': 'Transaction deleted successfully'})

def coupons_api(request):
    if request.method == 'GET':
        coupons = Coupon.objects.all().values()
        return JsonResponse(list(coupons), safe=False)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            coupon = Coupon.objects.create(
                code=data['code'],
                discount=data['discount'],
                is_percentage=data.get('is_percentage', False)
            )
            return JsonResponse({'id': coupon.id, 'code': coupon.code, 'discount': coupon.discount, 'active': coupon.active, 'is_percentage': coupon.is_percentage})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def coupon_api(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Coupon not found'}, status=404)

    if request.method == 'DELETE':
        coupon.delete()
        return JsonResponse({'message': 'Coupon deleted successfully'})
