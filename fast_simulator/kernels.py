"""Portfolio rules extracted from upstream ffe9409; daily sampling is fused.

These retain legacy withdrawal comparisons, rebalancing timing, fee offsets,
and company-model cash behavior. See MIGRATION.md for explicit corrections.
"""
import numpy as np
from numba import njit

@njit(cache=True, nogil=True)
def correlated_sample(mean, factor, df):
    n = len(mean)
    z = np.empty(n)
    for i in range(n):
        z[i] = np.random.normal()
    scale = np.sqrt(df / np.random.chisquare(df)) if n else 1.0
    out = np.empty(n)
    for i in range(n):
        value = 0.0
        for j in range(n):
            value += factor[i, j] * z[j]
        out[i] = value * scale
    return (out, scale)

@njit(cache=True, nogil=True)
def index_multipliers(mean, factor, active, fee_drag):
    values, scale = correlated_sample(mean, factor, 6.0)
    out = np.ones(13)
    for i in range(len(active)):
        k = active[i]
        out[k] = np.exp(values[i] + mean[i] * scale) * fee_drag[k]
    return out

@njit(cache=True, nogil=True)
def fund_returns(mean, factor, active):
    values, scale = correlated_sample(mean, factor, 5.0)
    out = np.zeros(13)
    for i in range(len(active)):
        out[active[i]] = values[i] + mean[i]
    return out

@njit(cache=True, nogil=True)
def index_path(acum_years, duration, matured_duration, assets, savings_account, pure_cash_amt, contribution_weights, inserted_funds, savings_account_weight, saving_daily_return, withdrawal_percentage, daily_hazard_rate, pure_cash_weight, us_gov_bond, us_inv_bond, us_spec_bond, thai_gov_bond, thai_inv_bond, thai_spec_bond, us_gov_bond_daily_return, us_inv_bond_daily_return, us_spec_bond_daily_return, thai_gov_bond_daily_return, thai_inv_bond_daily_return, thai_spec_bond_daily_return, stock_allocations, bond_mutualfund_allocation, hybrid_mutualfund_aggresive_allocation, hybrid_mutualfund_moderate_allocation, hybrid_mutualfund_conservative_allocation, target, bull_mean, bear_mean, bull_factor, bear_factor, active, fee_drag):
    has_direct_bonds = us_gov_bond + us_inv_bond + us_spec_bond + thai_gov_bond + thai_inv_bond + thai_spec_bond > 0
    goal_count = 0
    portfolio_path = np.zeros(duration, dtype=np.float32)
    thai_default_events = False
    us_default_events = False
    matured = False
    market = np.random.randint(0, 2)
    failed = 0
    for day in range(duration):
        if market == 1:
            current = index_multipliers(bear_mean, bear_factor, active, fee_drag)
            if np.random.random() < 0.05:
                market = 0
        else:
            current = index_multipliers(bull_mean, bull_factor, active, fee_drag)
            if np.random.random() < 0.02:
                market = 1
        assets *= current
        savings_account *= saving_daily_return
        if has_direct_bonds and day < acum_years * 252:
            if not thai_default_events and np.random.random() < daily_hazard_rate:
                thai_default_events = True
            if not us_default_events and np.random.random() < daily_hazard_rate:
                us_default_events = True
        if has_direct_bonds and (not matured):
            us_gov_bond *= us_gov_bond_daily_return
            us_inv_bond *= us_inv_bond_daily_return
            thai_gov_bond *= thai_gov_bond_daily_return
            thai_inv_bond *= thai_inv_bond_daily_return
            if thai_default_events:
                thai_spec_bond = 0.0
            else:
                thai_spec_bond *= thai_spec_bond_daily_return
            if us_default_events:
                us_spec_bond = 0.0
            else:
                us_spec_bond *= us_spec_bond_daily_return
        if day % 21 == 0:
            if day < acum_years * 252:
                pure_cash_amt += inserted_funds * pure_cash_weight
                assets += inserted_funds * contribution_weights
                savings_account += inserted_funds * savings_account_weight
            else:
                total_amount = pure_cash_amt + savings_account + assets.sum()
                withdrawal_amount = withdrawal_percentage / 12.0
                if pure_cash_amt >= withdrawal_amount:
                    pure_cash_amt -= withdrawal_amount
                elif savings_account >= withdrawal_amount:
                    savings_account -= withdrawal_amount
                elif assets[4] >= withdrawal_amount:
                    assets[4] -= withdrawal_amount
                elif assets[5] >= withdrawal_amount:
                    assets[5] -= withdrawal_amount
                elif assets[3] >= withdrawal_amount:
                    assets[3] -= withdrawal_amount
                elif assets[0] >= withdrawal_amount:
                    assets[0] -= withdrawal_amount
                elif assets[2] >= withdrawal_amount:
                    assets[2] -= withdrawal_amount
                elif assets[1] >= withdrawal_amount:
                    assets[1] -= withdrawal_amount
                elif assets[7] >= withdrawal_amount:
                    assets[7] -= withdrawal_amount
                elif assets[8] >= withdrawal_amount:
                    assets[8] -= withdrawal_amount
                elif assets[9] >= withdrawal_amount:
                    assets[9] -= withdrawal_amount
                elif assets[10] >= withdrawal_amount:
                    assets[10] -= withdrawal_amount
                elif assets[11] >= withdrawal_amount:
                    assets[11] -= withdrawal_amount
                elif assets[12] >= withdrawal_amount:
                    assets[12] -= withdrawal_amount
                elif assets[6] >= withdrawal_amount:
                    assets[6] -= withdrawal_amount
                elif total_amount >= withdrawal_amount:
                    total_amount -= withdrawal_amount
                    assets = total_amount * contribution_weights
                    pure_cash_amt = total_amount * pure_cash_weight
                    savings_account = total_amount * savings_account_weight
                else:
                    failed = 1
                    break
        if has_direct_bonds and (not matured and day > 0 and (day % matured_duration == 0)):
            matured = True
            pure_cash_amt += us_gov_bond + us_inv_bond + thai_gov_bond + thai_inv_bond + thai_spec_bond + us_spec_bond
            us_gov_bond = 0.0
            us_inv_bond = 0.0
            thai_gov_bond = 0.0
            thai_inv_bond = 0.0
            thai_spec_bond = 0.0
            us_spec_bond = 0.0
        if day % 252 == 0:
            cur_amount = pure_cash_amt + savings_account + assets.sum()
            pure_cash_amt = cur_amount * pure_cash_weight
            savings_account = cur_amount * savings_account_weight
            assets = np.array([cur_amount * stock_allocations[0], cur_amount * stock_allocations[1], cur_amount * stock_allocations[2], cur_amount * bond_mutualfund_allocation, cur_amount * hybrid_mutualfund_aggresive_allocation, cur_amount * hybrid_mutualfund_moderate_allocation, cur_amount * hybrid_mutualfund_conservative_allocation, cur_amount * stock_allocations[3], cur_amount * stock_allocations[4], cur_amount * stock_allocations[5], cur_amount * stock_allocations[6], cur_amount * stock_allocations[7], cur_amount * stock_allocations[8]], dtype=np.float64)
        if day == acum_years * 252:
            cur_amount = pure_cash_amt + savings_account + assets.sum()
            if cur_amount >= target:
                goal_count = 1
            else:
                goal_count = 0
        portfolio_path[day] = assets[0] + assets[1] + assets[2] + assets[3] + assets[4] + assets[5] + assets[6] + assets[7] + assets[8] + assets[9] + assets[10] + assets[11] + assets[12] + savings_account + pure_cash_amt
    return (portfolio_path, failed, goal_count)

@njit(cache=True, nogil=True)
def fund_path(acum_years, duration, inserted_funds, yearly_withdrawals, gqg_amt, kkpplus_amt, kkpcash_amt, kfa_amt, ugi_amt, gtech_amt, eae_amt, ktp_amt, savings_amt, rostrum_amt, gnph_amt, healthcarea_amt, propa_amt, sp500a_amt, gcore_amt, kkpplus_alloc, kkpcash_alloc, kfa_alloc, ugi_alloc, gqg_alloc, gtech_alloc, eae_alloc, ktprecious_alloc, savings_alloc, rostrum_alloc, gnph_alloc, healthcarea_alloc, propa_alloc, sp500a_alloc, gcore_alloc, target, mean, factor, active, rostrum_daily, fof_vol):
    goal_count = 0
    portfolio_paths = np.zeros(duration)
    failed = 0
    for day in range(duration):
        returns = fund_returns(mean, factor, active)
        rostrum_return = rostrum_daily
        if rostrum_alloc > 0:
            rostrum_return += 1.75 * fof_vol * np.random.standard_t(10)
        gqg_amt *= np.exp(returns[1] - 0.0002)
        gtech_amt *= np.exp(returns[3] - 0.001875)
        eae_amt *= np.exp(returns[2] - 0.001)
        ktp_amt *= np.exp(returns[0] - 0.00185)
        ugi_amt *= np.exp(returns[9])
        kkpplus_amt *= np.exp(returns[6])
        kkpcash_amt *= np.exp(returns[7])
        kfa_amt *= np.exp(returns[8])
        rostrum_amt *= rostrum_return
        gnph_amt *= np.exp(returns[4] - 0.0002)
        healthcarea_amt *= np.exp(returns[10] - 0.0001)
        propa_amt *= np.exp(returns[11])
        sp500a_amt *= np.exp(returns[12] - 0.0002)
        gcore_amt *= np.exp(returns[5] - 0.00034)
        savings_amt = savings_amt
        if day < acum_years * 252 and day % 21 == 0:
            kkpplus_amt += inserted_funds * kkpplus_alloc
            kkpcash_amt += inserted_funds * kkpcash_alloc
            kfa_amt += inserted_funds * kfa_alloc
            ugi_amt += inserted_funds * ugi_alloc
            gqg_amt += inserted_funds * gqg_alloc
            gtech_amt += inserted_funds * gtech_alloc
            eae_amt += inserted_funds * eae_alloc
            ktp_amt += inserted_funds * ktprecious_alloc
            savings_amt += inserted_funds * savings_alloc
            rostrum_amt += inserted_funds * rostrum_alloc
            gnph_amt += inserted_funds * gnph_alloc
            healthcarea_amt += inserted_funds * healthcarea_alloc
            propa_amt += inserted_funds * propa_alloc
            sp500a_amt += inserted_funds * sp500a_alloc
            gcore_amt += inserted_funds * gcore_alloc
        if day > acum_years * 252 and day % 21 == 0:
            curnt_amt = kkpplus_amt + kkpcash_amt + kfa_amt + ugi_amt + gqg_amt + gtech_amt + eae_amt + ktp_amt + rostrum_amt + gnph_amt + healthcarea_amt + propa_amt + sp500a_amt + savings_amt + gcore_amt
            withdrawal_amount = yearly_withdrawals / 12
            if savings_amt - withdrawal_amount > 0:
                savings_amt = savings_amt - withdrawal_amount
            elif kfa_amt - withdrawal_amount > 0:
                kfa_amt = kfa_amt - withdrawal_amount
            elif ugi_amt - withdrawal_amount > 0:
                ugi_amt = ugi_amt - withdrawal_amount
            elif kkpplus_amt - withdrawal_amount > 0:
                kkpplus_amt = kkpplus_amt - withdrawal_amount
            elif kkpcash_amt - withdrawal_amount > 0:
                kkpcash_amt = kkpcash_amt - withdrawal_amount
            elif gqg_amt - withdrawal_amount > 0:
                gqg_amt = gqg_amt - withdrawal_amount
            elif gtech_amt - withdrawal_amount > 0:
                gtech_amt = gtech_amt - withdrawal_amount
            elif eae_amt - withdrawal_amount > 0:
                eae_amt = eae_amt - withdrawal_amount
            elif gcore_amt - withdrawal_amount > 0:
                gcore_amt = gcore_amt - withdrawal_amount
            elif ktp_amt - withdrawal_amount > 0:
                ktp_amt = ktp_amt - withdrawal_amount
            elif rostrum_amt - withdrawal_amount > 0:
                rostrum_amt = rostrum_amt - withdrawal_amount
            elif gnph_amt - withdrawal_amount > 0:
                gnph_amt = gnph_amt - withdrawal_amount
            elif healthcarea_amt - withdrawal_amount > 0:
                healthcarea_amt = healthcarea_amt - withdrawal_amount
            elif propa_amt - withdrawal_amount > 0:
                propa_amt = propa_amt - withdrawal_amount
            elif sp500a_amt - withdrawal_amount > 0:
                sp500a_amt = sp500a_amt - withdrawal_amount
            elif curnt_amt - withdrawal_amount > 0:
                curnt_amt -= withdrawal_amount
                savings_amt = curnt_amt * savings_alloc
                kfa_amt = curnt_amt * kfa_alloc
                ugi_amt = curnt_amt * ugi_alloc
                kkpplus_amt = curnt_amt * kkpplus_alloc
                kkpcash_amt = curnt_amt * kkpcash_alloc
                gqg_amt = curnt_amt * gqg_alloc
                eae_amt = curnt_amt * eae_alloc
                gtech_amt = curnt_amt * gtech_alloc
                gcore_amt = curnt_amt * gcore_alloc
                ktp_amt = curnt_amt * ktprecious_alloc
                rostrum_amt = curnt_amt * rostrum_alloc
                gnph_amt = curnt_amt * gnph_alloc
                healthcarea_amt = curnt_amt * healthcarea_alloc
                propa_amt = curnt_amt * propa_alloc
                sp500a_amt = curnt_amt * sp500a_alloc
            else:
                failed = 1
                break
        if day % 252 == 0:
            curnt_amt = kkpplus_amt + kkpcash_amt + kfa_amt + ugi_amt + gqg_amt + gtech_amt + eae_amt + ktp_amt + rostrum_amt + gnph_amt + healthcarea_amt + propa_amt + sp500a_amt + savings_amt + gcore_amt
            if curnt_amt * rostrum_alloc < 3000000 and rostrum_alloc != 0:
                savings_alloc += rostrum_alloc
                rostrum_alloc = 0
            kkpplus_amt = curnt_amt * kkpplus_alloc
            kkpcash_amt = curnt_amt * kkpcash_alloc
            kfa_amt = curnt_amt * kfa_alloc
            ugi_amt = curnt_amt * ugi_alloc
            gqg_amt = curnt_amt * gqg_alloc
            gtech_amt = curnt_amt * gtech_alloc
            eae_amt = curnt_amt * eae_alloc
            ktp_amt = curnt_amt * ktprecious_alloc
            savings_amt = curnt_amt * savings_alloc
            rostrum_amt = curnt_amt * rostrum_alloc
            gcore_amt = curnt_amt * gcore_alloc
            gnph_amt = curnt_amt * gnph_alloc
            healthcarea_amt = curnt_amt * healthcarea_alloc
            propa_amt = curnt_amt * propa_alloc
            sp500a_amt = curnt_amt * sp500a_alloc
        portfolio_paths[day] = kkpplus_amt + kkpcash_amt + kfa_amt + ugi_amt + gqg_amt + gtech_amt + eae_amt + ktp_amt + savings_amt + rostrum_amt + gnph_amt + healthcarea_amt + propa_amt + sp500a_amt + gcore_amt
        if day == acum_years * 252:
            curnt_amt = kkpplus_amt + kkpcash_amt + kfa_amt + ugi_amt + gqg_amt + gtech_amt + eae_amt + ktp_amt + rostrum_amt + gnph_amt + healthcarea_amt + propa_amt + sp500a_amt + savings_amt + gcore_amt
            if curnt_amt >= target:
                goal_count = 1
            else:
                goal_count = 0
    return (portfolio_paths, failed, goal_count)

@njit(cache=True, nogil=True)
def index_cached_path(acum_years, duration, matured_duration, assets, savings_account, pure_cash_amt, contribution_weights, inserted_funds, savings_account_weight, saving_daily_return, withdrawal_percentage, daily_hazard_rate, pure_cash_weight, us_gov_bond, us_inv_bond, us_spec_bond, thai_gov_bond, thai_inv_bond, thai_spec_bond, us_gov_bond_daily_return, us_inv_bond_daily_return, us_spec_bond_daily_return, thai_gov_bond_daily_return, thai_inv_bond_daily_return, thai_spec_bond_daily_return, stock_allocations, bond_mutualfund_allocation, hybrid_mutualfund_aggresive_allocation, hybrid_mutualfund_moderate_allocation, hybrid_mutualfund_conservative_allocation, target, bull_mean, bear_mean, bull_factor, bear_factor, active, fee_drag, scenarios):
    has_direct_bonds = us_gov_bond + us_inv_bond + us_spec_bond + thai_gov_bond + thai_inv_bond + thai_spec_bond > 0
    goal_count = 0
    portfolio_path = np.zeros(duration, dtype=np.float32)
    thai_default_events = False
    us_default_events = False
    matured = False
    market = np.random.randint(0, 2)
    failed = 0
    for day in range(duration):
        for asset in range(13):
            assets[asset] *= scenarios[day, asset]
        savings_account *= saving_daily_return
        if has_direct_bonds and day < acum_years * 252:
            if not thai_default_events and np.random.random() < daily_hazard_rate:
                thai_default_events = True
            if not us_default_events and np.random.random() < daily_hazard_rate:
                us_default_events = True
        if has_direct_bonds and (not matured):
            us_gov_bond *= us_gov_bond_daily_return
            us_inv_bond *= us_inv_bond_daily_return
            thai_gov_bond *= thai_gov_bond_daily_return
            thai_inv_bond *= thai_inv_bond_daily_return
            if thai_default_events:
                thai_spec_bond = 0.0
            else:
                thai_spec_bond *= thai_spec_bond_daily_return
            if us_default_events:
                us_spec_bond = 0.0
            else:
                us_spec_bond *= us_spec_bond_daily_return
        if day % 21 == 0:
            if day < acum_years * 252:
                pure_cash_amt += inserted_funds * pure_cash_weight
                for asset in range(13):
                    assets[asset] += inserted_funds * contribution_weights[asset]
                savings_account += inserted_funds * savings_account_weight
            else:
                total_amount = pure_cash_amt + savings_account + assets.sum()
                withdrawal_amount = withdrawal_percentage / 12.0
                if pure_cash_amt >= withdrawal_amount:
                    pure_cash_amt -= withdrawal_amount
                elif savings_account >= withdrawal_amount:
                    savings_account -= withdrawal_amount
                elif assets[4] >= withdrawal_amount:
                    assets[4] -= withdrawal_amount
                elif assets[5] >= withdrawal_amount:
                    assets[5] -= withdrawal_amount
                elif assets[3] >= withdrawal_amount:
                    assets[3] -= withdrawal_amount
                elif assets[0] >= withdrawal_amount:
                    assets[0] -= withdrawal_amount
                elif assets[2] >= withdrawal_amount:
                    assets[2] -= withdrawal_amount
                elif assets[1] >= withdrawal_amount:
                    assets[1] -= withdrawal_amount
                elif assets[7] >= withdrawal_amount:
                    assets[7] -= withdrawal_amount
                elif assets[8] >= withdrawal_amount:
                    assets[8] -= withdrawal_amount
                elif assets[9] >= withdrawal_amount:
                    assets[9] -= withdrawal_amount
                elif assets[10] >= withdrawal_amount:
                    assets[10] -= withdrawal_amount
                elif assets[11] >= withdrawal_amount:
                    assets[11] -= withdrawal_amount
                elif assets[12] >= withdrawal_amount:
                    assets[12] -= withdrawal_amount
                elif assets[6] >= withdrawal_amount:
                    assets[6] -= withdrawal_amount
                elif total_amount >= withdrawal_amount:
                    total_amount -= withdrawal_amount
                    for asset in range(13):
                        assets[asset] = total_amount * contribution_weights[asset]
                    pure_cash_amt = total_amount * pure_cash_weight
                    savings_account = total_amount * savings_account_weight
                else:
                    failed = 1
                    break
        if has_direct_bonds and (not matured and day > 0 and (day % matured_duration == 0)):
            matured = True
            pure_cash_amt += us_gov_bond + us_inv_bond + thai_gov_bond + thai_inv_bond + thai_spec_bond + us_spec_bond
            us_gov_bond = 0.0
            us_inv_bond = 0.0
            thai_gov_bond = 0.0
            thai_inv_bond = 0.0
            thai_spec_bond = 0.0
            us_spec_bond = 0.0
        if day % 252 == 0:
            cur_amount = pure_cash_amt + savings_account + assets.sum()
            pure_cash_amt = cur_amount * pure_cash_weight
            savings_account = cur_amount * savings_account_weight
            for asset in range(13):
                assets[asset] = cur_amount * contribution_weights[asset]
        if day == acum_years * 252:
            cur_amount = pure_cash_amt + savings_account + assets.sum()
            if cur_amount >= target:
                goal_count = 1
            else:
                goal_count = 0
        portfolio_path[day] = assets[0] + assets[1] + assets[2] + assets[3] + assets[4] + assets[5] + assets[6] + assets[7] + assets[8] + assets[9] + assets[10] + assets[11] + assets[12] + savings_account + pure_cash_amt
    return (portfolio_path, failed, goal_count)

@njit(cache=True, nogil=True)
def fund_cached_path(acum_years, duration, inserted_funds, yearly_withdrawals, gqg_amt, kkpplus_amt, kkpcash_amt, kfa_amt, ugi_amt, gtech_amt, eae_amt, ktp_amt, savings_amt, rostrum_amt, gnph_amt, healthcarea_amt, propa_amt, sp500a_amt, gcore_amt, kkpplus_alloc, kkpcash_alloc, kfa_alloc, ugi_alloc, gqg_alloc, gtech_alloc, eae_alloc, ktprecious_alloc, savings_alloc, rostrum_alloc, gnph_alloc, healthcarea_alloc, propa_alloc, sp500a_alloc, gcore_alloc, target, mean, factor, active, rostrum_daily, fof_vol, scenarios):
    goal_count = 0
    portfolio_paths = np.zeros(duration)
    failed = 0
    for day in range(duration):
        gqg_amt *= scenarios[day, 1]
        gtech_amt *= scenarios[day, 3]
        eae_amt *= scenarios[day, 2]
        ktp_amt *= scenarios[day, 0]
        ugi_amt *= scenarios[day, 9]
        kkpplus_amt *= scenarios[day, 6]
        kkpcash_amt *= scenarios[day, 7]
        kfa_amt *= scenarios[day, 8]
        rostrum_amt *= scenarios[day, 13]
        gnph_amt *= scenarios[day, 4]
        healthcarea_amt *= scenarios[day, 10]
        propa_amt *= scenarios[day, 11]
        sp500a_amt *= scenarios[day, 12]
        gcore_amt *= scenarios[day, 5]
        savings_amt = savings_amt
        if day < acum_years * 252 and day % 21 == 0:
            kkpplus_amt += inserted_funds * kkpplus_alloc
            kkpcash_amt += inserted_funds * kkpcash_alloc
            kfa_amt += inserted_funds * kfa_alloc
            ugi_amt += inserted_funds * ugi_alloc
            gqg_amt += inserted_funds * gqg_alloc
            gtech_amt += inserted_funds * gtech_alloc
            eae_amt += inserted_funds * eae_alloc
            ktp_amt += inserted_funds * ktprecious_alloc
            savings_amt += inserted_funds * savings_alloc
            rostrum_amt += inserted_funds * rostrum_alloc
            gnph_amt += inserted_funds * gnph_alloc
            healthcarea_amt += inserted_funds * healthcarea_alloc
            propa_amt += inserted_funds * propa_alloc
            sp500a_amt += inserted_funds * sp500a_alloc
            gcore_amt += inserted_funds * gcore_alloc
        if day > acum_years * 252 and day % 21 == 0:
            curnt_amt = kkpplus_amt + kkpcash_amt + kfa_amt + ugi_amt + gqg_amt + gtech_amt + eae_amt + ktp_amt + rostrum_amt + gnph_amt + healthcarea_amt + propa_amt + sp500a_amt + savings_amt + gcore_amt
            withdrawal_amount = yearly_withdrawals / 12
            if savings_amt - withdrawal_amount > 0:
                savings_amt = savings_amt - withdrawal_amount
            elif kfa_amt - withdrawal_amount > 0:
                kfa_amt = kfa_amt - withdrawal_amount
            elif ugi_amt - withdrawal_amount > 0:
                ugi_amt = ugi_amt - withdrawal_amount
            elif kkpplus_amt - withdrawal_amount > 0:
                kkpplus_amt = kkpplus_amt - withdrawal_amount
            elif kkpcash_amt - withdrawal_amount > 0:
                kkpcash_amt = kkpcash_amt - withdrawal_amount
            elif gqg_amt - withdrawal_amount > 0:
                gqg_amt = gqg_amt - withdrawal_amount
            elif gtech_amt - withdrawal_amount > 0:
                gtech_amt = gtech_amt - withdrawal_amount
            elif eae_amt - withdrawal_amount > 0:
                eae_amt = eae_amt - withdrawal_amount
            elif gcore_amt - withdrawal_amount > 0:
                gcore_amt = gcore_amt - withdrawal_amount
            elif ktp_amt - withdrawal_amount > 0:
                ktp_amt = ktp_amt - withdrawal_amount
            elif rostrum_amt - withdrawal_amount > 0:
                rostrum_amt = rostrum_amt - withdrawal_amount
            elif gnph_amt - withdrawal_amount > 0:
                gnph_amt = gnph_amt - withdrawal_amount
            elif healthcarea_amt - withdrawal_amount > 0:
                healthcarea_amt = healthcarea_amt - withdrawal_amount
            elif propa_amt - withdrawal_amount > 0:
                propa_amt = propa_amt - withdrawal_amount
            elif sp500a_amt - withdrawal_amount > 0:
                sp500a_amt = sp500a_amt - withdrawal_amount
            elif curnt_amt - withdrawal_amount > 0:
                curnt_amt -= withdrawal_amount
                savings_amt = curnt_amt * savings_alloc
                kfa_amt = curnt_amt * kfa_alloc
                ugi_amt = curnt_amt * ugi_alloc
                kkpplus_amt = curnt_amt * kkpplus_alloc
                kkpcash_amt = curnt_amt * kkpcash_alloc
                gqg_amt = curnt_amt * gqg_alloc
                eae_amt = curnt_amt * eae_alloc
                gtech_amt = curnt_amt * gtech_alloc
                gcore_amt = curnt_amt * gcore_alloc
                ktp_amt = curnt_amt * ktprecious_alloc
                rostrum_amt = curnt_amt * rostrum_alloc
                gnph_amt = curnt_amt * gnph_alloc
                healthcarea_amt = curnt_amt * healthcarea_alloc
                propa_amt = curnt_amt * propa_alloc
                sp500a_amt = curnt_amt * sp500a_alloc
            else:
                failed = 1
                break
        if day % 252 == 0:
            curnt_amt = kkpplus_amt + kkpcash_amt + kfa_amt + ugi_amt + gqg_amt + gtech_amt + eae_amt + ktp_amt + rostrum_amt + gnph_amt + healthcarea_amt + propa_amt + sp500a_amt + savings_amt + gcore_amt
            if curnt_amt * rostrum_alloc < 3000000 and rostrum_alloc != 0:
                savings_alloc += rostrum_alloc
                rostrum_alloc = 0
            kkpplus_amt = curnt_amt * kkpplus_alloc
            kkpcash_amt = curnt_amt * kkpcash_alloc
            kfa_amt = curnt_amt * kfa_alloc
            ugi_amt = curnt_amt * ugi_alloc
            gqg_amt = curnt_amt * gqg_alloc
            gtech_amt = curnt_amt * gtech_alloc
            eae_amt = curnt_amt * eae_alloc
            ktp_amt = curnt_amt * ktprecious_alloc
            savings_amt = curnt_amt * savings_alloc
            rostrum_amt = curnt_amt * rostrum_alloc
            gcore_amt = curnt_amt * gcore_alloc
            gnph_amt = curnt_amt * gnph_alloc
            healthcarea_amt = curnt_amt * healthcarea_alloc
            propa_amt = curnt_amt * propa_alloc
            sp500a_amt = curnt_amt * sp500a_alloc
        portfolio_paths[day] = kkpplus_amt + kkpcash_amt + kfa_amt + ugi_amt + gqg_amt + gtech_amt + eae_amt + ktp_amt + savings_amt + rostrum_amt + gnph_amt + healthcarea_amt + propa_amt + sp500a_amt + gcore_amt
        if day == acum_years * 252:
            curnt_amt = kkpplus_amt + kkpcash_amt + kfa_amt + ugi_amt + gqg_amt + gtech_amt + eae_amt + ktp_amt + rostrum_amt + gnph_amt + healthcarea_amt + propa_amt + sp500a_amt + savings_amt + gcore_amt
            if curnt_amt >= target:
                goal_count = 1
            else:
                goal_count = 0
    return (portfolio_paths, failed, goal_count)
