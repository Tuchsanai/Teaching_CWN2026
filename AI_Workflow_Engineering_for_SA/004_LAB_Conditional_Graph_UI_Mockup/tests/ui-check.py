#!/usr/bin/env python3
"""Offline UI smoke checks. JSON edge compares failed IDs, not AI opinions.

Each decorated check catches its own failures, and the runner also catches
context/navigation/screenshot failures. No result here certifies LAN or security.
"""
import argparse
from datetime import datetime, timedelta
from functools import wraps
import json
import os
from pathlib import Path
import re
import sys

from playwright.sync_api import sync_playwright, expect


# Static selector inventory (dynamic menu-item-<id> follows the contract):
# data-testid="account-message"
# data-testid="account-pin"
# data-testid="account-role"
# data-testid="account-username"
# data-testid="active-table"
# data-testid="admin-menu-name"
# data-testid="admin-menu-price"
# data-testid="admin-menu-select"
# data-testid="admin-option-name"
# data-testid="admin-option-price"
# data-testid="auth-message"
# data-testid="btn-add-item"
# data-testid="btn-advance-10m"
# data-testid="btn-close-table"
# data-testid="btn-confirm-slip"
# data-testid="btn-delete-menu"
# data-testid="btn-login"
# data-testid="btn-open-menu"
# data-testid="btn-receive-cash"
# data-testid="btn-reset"
# data-testid="btn-save-account"
# data-testid="btn-save-mapping"
# data-testid="btn-save-menu"
# data-testid="btn-status-next"
# data-testid="btn-submit-order"
# data-testid="cart-count"
# data-testid="cart-total"
# data-testid="cash-message"
# data-testid="customer-order-status"
# data-testid="front-orders"
# data-testid="front-payment-status"
# data-testid="front-table-select"
# data-testid="front-total"
# data-testid="ingredient-select"
# data-testid="ingredient-status"
# data-testid="item-total"
# data-testid="kitchen-order"
# data-testid="kitchen-queue"
# data-testid="mapping-ingredient"
# data-testid="mapping-list"
# data-testid="mapping-menu"
# data-testid="mapping-option"
# data-testid="mapping-scope"
# data-testid="menu-admin"
# data-testid="menu-item-m01"
# data-testid="menu-item-m02"
# data-testid="menu-item-m09"
# data-testid="menu-list"
# data-testid="nav-accounts"
# data-testid="nav-front"
# data-testid="nav-kitchen"
# data-testid="nav-mapping"
# data-testid="nav-menu-admin"
# data-testid="option-extra-egg"
# data-testid="order-id"
# data-testid="order-message"
# data-testid="order-mode"
# data-testid="pay-cash"
# data-testid="pay-promptpay"
# data-testid="payment-log"
# data-testid="payment-status"
# data-testid="pickup-slot"
# data-testid="role-customer"
# data-testid="role-manager"
# data-testid="role-staff"
# data-testid="screen-customer"
# data-testid="screen-manager"
# data-testid="session-id"
# data-testid="sim-clock"
# data-testid="staff-pin"
# data-testid="staff-user"
# data-testid="table-select"
# data-testid="takeaway-id"
# data-testid="toggle-promptpay"

CHECKS = []
TIMEOUT = 2500


def checked(check_id, *us):
    def decorate(fn):
        @wraps(fn)
        def guarded(page):
            try:
                fn(page)
                return {"id": check_id, "us": list(us), "passed": True,
                        "detail": "Observed all assertions; mock behavior only."}
            except Exception as exc:
                return {"id": check_id, "us": list(us), "passed": False,
                        "detail": f"{type(exc).__name__}: {exc}"[:2400]}
        CHECKS.append((check_id, list(us), guarded))
        return guarded
    return decorate


def ui(page, testid):
    return page.get_by_test_id(testid)


def click(page, testid):
    ui(page, testid).click()


def money(locator):
    text = locator.inner_text().replace(',', '')
    values = re.findall(r'\d+(?:\.\d+)?', text)
    assert len(values) == 1, f"Expected one displayed amount, got {text!r}"
    return float(values[0])


def login(page, role):
    click(page, 'role-manager' if role == 'manager' else 'role-staff')
    ui(page, 'staff-user').select_option('demo' + role)
    ui(page, 'staff-pin').fill('0000')
    click(page, 'btn-login')
    if role in ('kitchen', 'front'):
        click(page, 'nav-' + role)
    else:
        expect(ui(page, 'screen-manager')).to_be_visible()


def customer(page, table='01'):
    click(page, 'role-customer')
    ui(page, 'table-select').select_option(table)
    click(page, 'btn-open-menu')
    expect(ui(page, 'menu-list')).to_be_visible()


def add_item(page, menu='m01', egg=False):
    click(page, 'menu-item-' + menu)
    if egg:
        ui(page, 'option-extra-egg').check()
    click(page, 'btn-add-item')


def submit(page, menu='m01', egg=False):
    add_item(page, menu, egg)
    click(page, 'btn-submit-order')
    expect(ui(page, 'cart-count')).to_have_text('0')
    order_id = ui(page, 'order-id').inner_text().strip()
    assert order_id.isdigit(), f'Order ID must be numeric: {order_id!r}'
    return order_id


def stock(page, ingredient, available):
    login(page, 'kitchen')
    ui(page, 'ingredient-select').select_option(ingredient)
    click(page, 'btn-restock' if available else 'btn-out-of-stock')
    expect(ui(page, 'ingredient-status')).to_contain_text('มี' if available else 'หมด')


def order_row(page, container, order_id):
    # data-order-id is an integer read from the UI, never an arbitrary selector.
    assert order_id.isdigit()
    return ui(page, container).locator(f'[data-order-id="{order_id}"]')


@checked('roles', 'US-01', 'US-25')
def check_role_switch(page):
    expect(ui(page, 'role-customer')).to_be_visible()
    expect(ui(page, 'role-staff')).to_be_visible()
    expect(ui(page, 'role-manager')).to_be_visible()
    customer(page)
    expect(ui(page, 'screen-customer')).to_be_visible()
    login(page, 'kitchen')
    expect(ui(page, 'kitchen-queue')).to_be_visible()
    login(page, 'front')
    expect(ui(page, 'front-orders')).to_be_visible()
    login(page, 'manager')
    click(page, 'nav-menu-admin')
    expect(ui(page, 'menu-admin')).to_be_visible()


@checked('table-menu', 'US-01', 'US-02')
def check_table_menu(page):
    customer(page, '02')
    expect(ui(page, 'active-table')).to_contain_text('02')
    expect(ui(page, 'menu-item-m01')).to_be_enabled()
    oid = submit(page)
    login(page, 'front')
    expect(order_row(page, 'front-orders', oid)).to_have_attribute('data-table-id', '02')


@checked('option-price', 'US-04')
def check_option_price(page):
    customer(page)
    click(page, 'menu-item-m01')
    assert money(ui(page, 'item-total')) == 50
    ui(page, 'option-extra-egg').check()
    expect(ui(page, 'item-total')).to_contain_text('60')
    assert money(ui(page, 'item-total')) == 60
    click(page, 'btn-add-item')
    assert money(ui(page, 'cart-total')) == 60
    click(page, 'btn-submit-order')
    oid = ui(page, 'order-id').inner_text().strip()
    login(page, 'kitchen')
    expect(order_row(page, 'kitchen-queue', oid)).to_contain_text('เพิ่มไข่ดาว')


@checked('queue-order', 'US-10')
def check_queue_order(page):
    customer(page)
    ids = [submit(page), submit(page, 'm02')]
    assert int(ids[1]) == int(ids[0]) + 1, f'Non-monotonic IDs: {ids}'
    login(page, 'kitchen')
    rows = ui(page, 'kitchen-queue').get_by_test_id('kitchen-order')
    expect(rows).to_have_count(2)
    observed = [rows.nth(i).get_attribute('data-order-id') for i in range(2)]
    assert observed == ids, f'Queue {observed} != submission {ids}'
    times = [datetime.fromisoformat(rows.nth(i).get_attribute('data-received-at')) for i in range(2)]
    assert all(t.tzinfo and t.microsecond == 0 for t in times)
    # Simulation clock is frozen: this explicitly tests the equal-second tie.
    assert times[0] == times[1], f'Fixture must freeze time, got {times}'
    assert sorted(zip(times, map(int, observed))) == list(zip(times, map(int, ids)))


@checked('status-sync', 'US-05', 'US-11')
def check_status_sync(page):
    customer(page)
    oid = submit(page)
    expect(ui(page, 'customer-order-status')).to_have_text('รับออเดอร์')
    for status in ('กำลังทำ', 'เสร็จแล้ว'):
        login(page, 'kitchen')
        order_row(page, 'kitchen-queue', oid).get_by_test_id('btn-status-next').click()
        click(page, 'role-customer')
        expect(ui(page, 'customer-order-status')).to_have_text(status)
        login(page, 'front')
        expect(order_row(page, 'front-orders', oid)).to_contain_text(status)


@checked('stock-whole', 'US-06', 'US-12')
def check_stock_whole(page):
    customer(page)
    add_item(page)  # Stale cart must be rejected at submit, not only disabled UI.
    stock(page, 'chicken', False)
    click(page, 'role-customer')
    expect(ui(page, 'menu-item-m01')).to_be_disabled()
    expect(ui(page, 'menu-list')).to_contain_text('หมด')
    click(page, 'btn-submit-order')
    expect(ui(page, 'order-message')).to_contain_text('หมด')
    login(page, 'kitchen')
    expect(ui(page, 'kitchen-queue').get_by_test_id('kitchen-order')).to_have_count(0)


@checked('stock-option', 'US-06', 'US-12')
def check_stock_option(page):
    customer(page)
    add_item(page, egg=True)
    stock(page, 'egg', False)
    click(page, 'role-customer')
    expect(ui(page, 'menu-item-m01')).to_be_enabled()
    click(page, 'menu-item-m01')
    expect(ui(page, 'option-extra-egg')).to_be_disabled()
    click(page, 'btn-submit-order')
    expect(ui(page, 'order-message')).to_contain_text('หมด')
    login(page, 'kitchen')
    expect(ui(page, 'kitchen-queue').get_by_test_id('kitchen-order')).to_have_count(0)


@checked('restock', 'US-13')
def check_restock(page):
    customer(page)
    stock(page, 'chicken', False)
    click(page, 'role-customer')
    expect(ui(page, 'menu-item-m01')).to_be_disabled()
    stock(page, 'chicken', True)
    stock(page, 'egg', False)
    click(page, 'role-customer')
    click(page, 'menu-item-m01')
    expect(ui(page, 'option-extra-egg')).to_be_disabled()
    stock(page, 'egg', True)
    click(page, 'role-customer')
    click(page, 'menu-item-m01')
    expect(ui(page, 'option-extra-egg')).to_be_enabled()
    ui(page, 'option-extra-egg').check()
    click(page, 'btn-add-item')
    click(page, 'btn-submit-order')
    login(page, 'kitchen')
    expect(ui(page, 'kitchen-queue').get_by_test_id('kitchen-order')).to_have_count(1)


@checked('promptpay-slip', 'US-08', 'US-15')
def check_promptpay_slip(page):
    customer(page)
    oid = submit(page, egg=True)
    expect(ui(page, 'payment-status')).to_have_text('ยังไม่จ่าย')
    click(page, 'pay-promptpay')
    expect(ui(page, 'payment-status')).to_have_text('ค้างจ่าย')
    login(page, 'front')
    row = order_row(page, 'front-orders', oid)
    expect(row.get_by_test_id('front-payment-status')).to_have_text('ค้างจ่าย')
    assert money(row.get_by_test_id('front-total')) == 60
    row.get_by_test_id('btn-confirm-slip').click()
    expect(row.get_by_test_id('front-payment-status')).to_have_text('จ่ายแล้ว')
    expect(ui(page, 'payment-log')).to_contain_text('demofront')
    expect(ui(page, 'payment-log')).to_contain_text(oid)
    expect(ui(page, 'payment-log')).to_contain_text(re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}'))
    click(page, 'role-customer')
    expect(ui(page, 'payment-status')).to_have_text('จ่ายแล้ว')


@checked('promptpay-disabled', 'US-08')
def check_promptpay_disabled(page):
    customer(page)
    submit(page)
    login(page, 'manager')
    ui(page, 'toggle-promptpay').uncheck()
    click(page, 'role-customer')
    expect(ui(page, 'cash-message')).to_contain_text('เงินสด')
    expect(ui(page, 'payment-status')).not_to_have_text('จ่ายแล้ว')


@checked('promptpay-timeout-cash', 'US-08', 'US-15')
def check_promptpay_timeout_cash(page):
    customer(page)
    oid = submit(page)
    click(page, 'pay-promptpay')
    click(page, 'btn-advance-10m')
    expect(ui(page, 'cash-message')).to_contain_text('เงินสด')
    expect(ui(page, 'payment-status')).to_have_text('ค้างจ่าย')
    click(page, 'pay-cash')
    expect(ui(page, 'payment-status')).not_to_have_text('จ่ายแล้ว')
    login(page, 'front')
    row = order_row(page, 'front-orders', oid)
    row.get_by_test_id('btn-receive-cash').click()
    expect(row.get_by_test_id('front-payment-status')).to_have_text('จ่ายแล้ว')
    expect(ui(page, 'payment-log')).to_contain_text('demofront')
    expect(ui(page, 'payment-log')).to_contain_text(re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}'))
    click(page, 'role-customer')
    expect(ui(page, 'payment-status')).to_have_text('จ่ายแล้ว')


@checked('takeaway-slot', 'US-03', 'US-15')
def check_takeaway_slot(page):
    customer(page)
    ui(page, 'order-mode').select_option('takeaway')
    now = datetime.fromisoformat(ui(page, 'sim-clock').inner_text().strip())
    values = ui(page, 'pickup-slot').locator('option').evaluate_all(
        '(nodes) => nodes.filter(n => !n.disabled && n.value).map(n => n.value)')
    assert len(values) >= 2, f'Need at least two pickup slots: {values}'
    starts = []
    for value in values:
        match = re.fullmatch(r'(\d{2}):(\d{2})-(\d{2}):(\d{2})', value)
        assert match, f'Bad slot: {value}'
        sh, sm, eh, em = map(int, match.groups())
        start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        end = start.replace(hour=eh, minute=em)
        if end <= start:
            end += timedelta(days=1)
        assert start >= now + timedelta(minutes=20)
        assert end - start == timedelta(minutes=15)
        starts.append(start)
    assert all(b-a == timedelta(minutes=15) for a,b in zip(starts, starts[1:]))
    ui(page, 'pickup-slot').select_option(values[0])
    oid = submit(page)
    expect(ui(page, 'takeaway-id')).to_have_text('T-001')
    login(page, 'kitchen')
    row = order_row(page, 'kitchen-queue', oid)
    expect(row).to_contain_text('สั่งกลับบ้าน')
    expect(row).to_contain_text(values[0])
    login(page, 'front')
    row = order_row(page, 'front-orders', oid)
    expect(row).to_contain_text('T-001')
    expect(row).to_have_attribute('data-table-id', 'takeaway')
    click(page, 'role-customer')
    submit(page, 'm02')
    expect(ui(page, 'takeaway-id')).to_have_text('T-002')


@checked('close-table', 'US-16')
def check_close_table(page):
    customer(page)
    old_session = ui(page, 'session-id').inner_text().strip()
    assert old_session
    oid = submit(page)
    login(page, 'front')
    order_row(page, 'front-orders', oid).get_by_test_id('btn-receive-cash').click()
    ui(page, 'front-table-select').select_option('01')
    click(page, 'btn-close-table')
    customer(page)
    new_session = ui(page, 'session-id').inner_text().strip()
    assert new_session and old_session != new_session
    expect(ui(page, 'cart-count')).to_have_text('0')
    expect(ui(page, 'order-id')).to_be_empty()
    expect(ui(page, 'payment-status')).to_have_text('ยังไม่จ่าย')
    new_oid = submit(page, 'm02')
    assert new_oid != oid
    login(page, 'front')
    assert money(order_row(page, 'front-orders', new_oid).get_by_test_id('front-total')) == 55


@checked('menu-management', 'US-19')
def check_menu_management(page):
    customer(page)
    oid = submit(page)
    login(page, 'manager')
    click(page, 'nav-menu-admin')
    ui(page, 'admin-menu-select').select_option('m01')
    ui(page, 'admin-menu-price').fill('65')
    click(page, 'btn-save-menu')
    click(page, 'role-customer')
    click(page, 'menu-item-m01')
    assert money(ui(page, 'item-total')) == 65
    login(page, 'front')
    assert money(order_row(page, 'front-orders', oid).get_by_test_id('front-total')) == 50
    login(page, 'manager')
    click(page, 'nav-menu-admin')
    ui(page, 'admin-menu-select').select_option('new')
    ui(page, 'admin-menu-name').fill('เมนูทดลอง')
    ui(page, 'admin-menu-price').fill('70')
    ui(page, 'admin-option-name').fill('เพิ่มพิเศษ')
    ui(page, 'admin-option-price').fill('5')
    click(page, 'btn-save-menu')
    click(page, 'role-customer')
    expect(ui(page, 'menu-item-m09')).to_contain_text('เมนูทดลอง')
    click(page, 'menu-item-m09')
    assert money(ui(page, 'item-total')) == 70
    login(page, 'manager')
    click(page, 'nav-menu-admin')
    ui(page, 'admin-menu-select').select_option('m09')
    click(page, 'btn-delete-menu')
    click(page, 'role-customer')
    expect(ui(page, 'menu-item-m09')).to_have_count(0)


@checked('ingredient-mapping', 'US-20', 'US-12', 'US-13')
def check_ingredient_mapping(page):
    customer(page)
    login(page, 'manager')
    click(page, 'nav-mapping')
    values = ui(page, 'mapping-menu').locator('option').evaluate_all(
        '(nodes) => nodes.filter(n => n.value).map(n => n.value)')
    assert set(values) == {f'm{i:02d}' for i in range(1, 9)}
    ui(page, 'mapping-menu').select_option('m02')
    ui(page, 'mapping-scope').select_option('whole')
    ui(page, 'mapping-ingredient').select_option('milk')
    click(page, 'btn-save-mapping')
    expect(ui(page, 'mapping-list')).to_contain_text('milk')
    stock(page, 'milk', False)
    click(page, 'role-customer')
    expect(ui(page, 'menu-item-m02')).to_be_disabled()
    expect(ui(page, 'menu-item-m01')).to_be_enabled()
    stock(page, 'milk', True)
    click(page, 'role-customer')
    expect(ui(page, 'menu-item-m02')).to_be_enabled()
    login(page, 'manager')
    click(page, 'nav-mapping')
    ui(page, 'mapping-menu').select_option('m01')
    ui(page, 'mapping-scope').select_option('option')
    ui(page, 'mapping-option').select_option('extra-egg')
    ui(page, 'mapping-ingredient').select_option('milk')
    click(page, 'btn-save-mapping')
    stock(page, 'milk', False)
    click(page, 'role-customer')
    expect(ui(page, 'menu-item-m01')).to_be_enabled()
    click(page, 'menu-item-m01')
    expect(ui(page, 'option-extra-egg')).to_be_disabled()


@checked('pin-lock', 'US-25')
def check_pin_lock(page):
    click(page, 'role-staff')
    ui(page, 'staff-user').select_option('demokitchen')
    for _ in range(5):
        ui(page, 'staff-pin').fill('9999')
        click(page, 'btn-login')
        expect(ui(page, 'auth-message')).to_contain_text(re.compile('ปฏิเสธ|ล็อก'))
    expect(ui(page, 'auth-message')).to_contain_text('ล็อก')
    ui(page, 'staff-pin').fill('0000')
    click(page, 'btn-login')
    expect(ui(page, 'auth-message')).to_contain_text('ล็อก')
    expect(ui(page, 'kitchen-queue')).not_to_be_visible()
    click(page, 'btn-advance-10m')
    ui(page, 'staff-pin').fill('0000')
    click(page, 'btn-login')
    click(page, 'nav-kitchen')
    expect(ui(page, 'kitchen-queue')).to_be_visible()


@checked('permission-denied', 'US-25')
def check_permission_denied(page):
    for role in ('kitchen', 'front'):
        login(page, role)
        for route, screen in (('/manager/menu', 'menu-admin'), ('/manager/reports', 'report-screen')):
            page.evaluate('(route) => { location.hash = route; }', route)
            expect(ui(page, 'auth-message')).to_contain_text('ปฏิเสธ')
            expect(ui(page, screen)).not_to_be_visible()
        page.evaluate('location.hash = ""')
    login(page, 'manager')
    click(page, 'nav-menu-admin')
    expect(ui(page, 'menu-admin')).to_be_visible()


@checked('account-create', 'US-25')
def check_account_create(page):
    login(page, 'manager')
    click(page, 'nav-accounts')
    ui(page, 'account-username').fill('ab')
    ui(page, 'account-pin').fill('123')
    ui(page, 'account-role').select_option('front')
    click(page, 'btn-save-account')
    expect(ui(page, 'account-message')).to_contain_text('ปฏิเสธ')
    ui(page, 'account-username').fill('demonew')
    ui(page, 'account-pin').fill('1234')
    click(page, 'btn-save-account')
    expect(ui(page, 'account-message')).to_contain_text('demonew')
    click(page, 'role-staff')
    ui(page, 'staff-user').select_option('demonew')
    ui(page, 'staff-pin').fill('1234')
    click(page, 'btn-login')
    click(page, 'nav-front')
    expect(ui(page, 'front-orders')).to_be_visible()
    page.evaluate('location.hash = "/manager/menu"')
    expect(ui(page, 'auth-message')).to_contain_text('ปฏิเสธ')
    expect(ui(page, 'menu-admin')).not_to_be_visible()


@checked('reset', 'US-02', 'US-16', 'US-25')
def check_reset(page):
    customer(page)
    submit(page)
    stock(page, 'chicken', False)
    login(page, 'manager')
    ui(page, 'toggle-promptpay').uncheck()
    click(page, 'btn-advance-10m')
    click(page, 'btn-reset')
    expect(ui(page, 'screen-customer')).to_be_visible()
    expect(ui(page, 'sim-clock')).to_have_text('2026-01-01T12:00:00+07:00')
    customer(page)
    expect(ui(page, 'cart-count')).to_have_text('0')
    expect(ui(page, 'order-id')).to_be_empty()
    expect(ui(page, 'payment-status')).to_have_text('ยังไม่จ่าย')
    expect(ui(page, 'menu-item-m01')).to_be_enabled()
    login(page, 'kitchen')
    expect(ui(page, 'kitchen-queue').get_by_test_id('kitchen-order')).to_have_count(0)
    login(page, 'manager')
    expect(ui(page, 'toggle-promptpay')).to_be_checked()


def decide_edge(checks, previous_failed=None):
    failed_ids = {c['id'] for c in checks if not c['passed']}
    if not failed_ids:
        return 'pass'
    if previous_failed is not None and failed_ids <= previous_failed and failed_ids == previous_failed:
        return 'cancel'
    return 'fix'


def read_previous(path):
    if path is None:
        return None
    previous = json.loads(Path(path).read_text(encoding='utf-8'))
    rows = previous['checks']
    expected = {cid for cid, _, _ in CHECKS}
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ValueError('--prev must contain the same complete check suite')
    if {c['id'] for c in rows} != expected or any(type(c['passed']) is not bool for c in rows):
        raise ValueError('--prev check IDs or passed booleans are invalid')
    failed_ids = {c['id'] for c in rows if not c['passed']}
    if previous.get('failed') != len(failed_ids) or previous.get('passed') != len(rows) - len(failed_ids):
        raise ValueError('--prev counts disagree with checks')
    return failed_ids


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', default='work/ui-mockup.html', help='Local offline HTML file')
    parser.add_argument('--out', default='work/ui-check-round-0.json', help='New JSON report path')
    parser.add_argument('--shots', default='work/shots/round-0', help='New/empty screenshot directory')
    parser.add_argument('--prev', help='Immediately previous JSON report; same failed IDs => cancel')
    args = parser.parse_args(argv)
    out, shots = Path(args.out), Path(args.shots)
    try:
        previous_failed = read_previous(args.prev)
        if out.exists():
            raise ValueError(f'Refusing to overwrite report: {out}')
        if shots.exists() and (not shots.is_dir() or any(shots.iterdir())):
            raise ValueError(f'Use a new or empty screenshot directory: {shots}')
        if out.resolve() == Path(args.html).resolve():
            raise ValueError('HTML and output must be different files')
        out.parent.mkdir(parents=True, exist_ok=True)
        shots.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        parser.error(str(exc))
    results, engine, launch_detail = [], 'unavailable', None
    browser = None
    infrastructure_error = False
    try:
        with sync_playwright() as p:
            try:
                try:
                    browser = p.chromium.launch()
                    engine = 'launch'
                except Exception as exc:
                    launch_detail = str(exc)[:1200]
                    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
                    engine = 'cdp'
                expect.set_options(timeout=TIMEOUT)
                for cid, us, run_check in CHECKS:
                    context = page = None
                    result = {'id': cid, 'us': us, 'passed': False, 'detail': 'Not started'}
                    blocked = []
                    try:
                        context = browser.new_context(viewport={'width': 1280, 'height': 900})
                        # Block network even if the generated HTML violates offline rules.
                        def route_request(route):
                            if route.request.url.startswith(('http://', 'https://')):
                                blocked.append(route.request.url)
                                route.abort()
                            else:
                                route.continue_()
                        context.route('**/*', route_request)
                        page = context.new_page()
                        page.set_default_timeout(TIMEOUT)
                        page.on('dialog', lambda dialog: dialog.accept())
                        page.goto('file://' + os.path.abspath(args.html))
                        click(page, 'btn-reset')
                        result = run_check(page)
                    except Exception as exc:
                        result['detail'] = f'Setup/runtime: {type(exc).__name__}: {exc}'[:2400]
                        infrastructure_error = True
                    finally:
                        if page is not None:
                            try:
                                page.screenshot(path=str(shots / f'{cid}.png'), full_page=True, timeout=5000)
                            except Exception as exc:
                                result['passed'] = False
                                result['detail'] += f'; screenshot unavailable: {exc}'[:500]
                        else:
                            result['detail'] += '; screenshot unavailable: no page'
                        if blocked:
                            result['passed'] = False
                            result['detail'] += '; offline violation: attempted network resources'
                        if context is not None:
                            try:
                                context.close()
                            except Exception as exc:
                                result['passed'] = False
                                result['detail'] += f'; context cleanup: {exc}'[:500]
                        results.append(result)
            finally:
                # Never close the externally supplied CDP browser or its existing tabs.
                if browser is not None and engine == 'launch':
                    browser.close()
    except Exception as exc:
        infrastructure_error = True
        completed = {r['id'] for r in results}
        for cid, us, _ in CHECKS:
            if cid not in completed:
                results.append({'id': cid, 'us': us, 'passed': False,
                                'detail': f'Infrastructure: {exc}; screenshot unavailable: no page'[:2400]})
        if len(completed) == len(CHECKS):
            results[-1]['passed'] = False
            results[-1]['detail'] += f'; browser cleanup: {exc}'[:500]
    passed = sum(c['passed'] for c in results)
    report = {'checks': results, 'passed': passed, 'failed': len(results) - passed,
              'edge': decide_edge(results, previous_failed), 'browser': engine,
              'launch_fallback_reason': launch_detail, 'html': os.path.abspath(args.html),
              'scope': 'mock smoke checks; no LAN, load or real security claim'}
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'failed': report['failed'],
                      'edge': report['edge'], 'out': str(out)}, ensure_ascii=False))
    return 0 if report['failed'] == 0 else (2 if infrastructure_error else 1)


if __name__ == '__main__':
    sys.exit(main())
