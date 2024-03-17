import BigNumber from 'bignumber.js';
import { BN } from '@coral-xyz/anchor';

// https://github.com/MikeMcl/bignumber.js
// https://blog.csdn.net/shenxianhui1995/article/details/103985434
export class TokenAmount {
  public wei: BigNumber;

  public decimals: number;
  public _decimals: BigNumber;

  // BN, Decimal, comparision.
  constructor(wei: number | string | BigNumber, decimals = 0, isWei = true) {
    this.decimals = decimals;
    this._decimals = new BigNumber(10).exponentiatedBy(decimals);

    if (isWei) {
      this.wei = new BigNumber(wei);
    } else {
      this.wei = new BigNumber(wei).multipliedBy(this._decimals);
    }
  }

  toEther() {
    return this.wei.dividedBy(this._decimals);
  }

  toWei() {
    return this.wei;
  }

  format() {
    const value = this.wei.dividedBy(this._decimals);
    return value.toFormat(value.isInteger() ? 0 : this.decimals);
  }

  fixed() {
    return this.wei
      .dividedBy(this._decimals)
      .toFixed(this.decimals)
      .replace(/(\.[0-9]*[1-9])0+$|\.0*$/, '$1');
  }

  fixedLocale(decimals?: number) {
    const result = this.wei
      .dividedBy(this._decimals)
      .toFixed(this.decimals)
      .replace(/(\.\d*[1-9])0+$|\.0*$/, '$1');
    if (decimals !== undefined) {
      return toLocale(toFixed(result, decimals));
    }
    return toLocale(result);
  }

  isNullOrZero() {
    return this.wei.isNaN() || this.wei.isZero();
  }

  toAnchorBN() {
    return new BN(this.wei.toString());
  }

  mul(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.multipliedBy(value);
  }

  div(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.dividedBy(value);
  }

  minus(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.minus(value);
  }

  plus(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.plus(value);
  }

  // BN
  lt(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.lt(value);
  }

  lte(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.lte(new BigNumber(value));
  }

  gt(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.gt(new BigNumber(value));
  }

  gte(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.gte(new BigNumber(value));
  }

  eq(a: number | string | BigNumber | TokenAmount) {
    const value = a instanceof TokenAmount ? a.toWei() : new BigNumber(a);
    return this.wei.eq(new BigNumber(value));
  }

  toNumber() {
    return this.wei.toNumber();
  }
}

// >
export function gt(a: string | number, b: string | number) {
  const valueA = new BigNumber(a);
  const valueB = new BigNumber(b);

  return valueA.isGreaterThan(valueB);
}

// >=
export function gte(a: string | number, b: string | number) {
  const valueA = new BigNumber(a);
  const valueB = new BigNumber(b);

  return valueA.isGreaterThanOrEqualTo(valueB);
}

// <
export function lt(a: string | number, b: string | number) {
  const valueA = new BigNumber(a);
  const valueB = new BigNumber(b);

  return valueA.isLessThan(valueB);
}

// <=
export function lte(a: string | number, b: string | number) {
  const valueA = new BigNumber(a);
  const valueB = new BigNumber(b);

  return valueA.isLessThanOrEqualTo(valueB);
}

export function isNullOrZero(value: string | number) {
  const amount = new BigNumber(value);

  return amount.isNaN() || amount.isZero();
}

export function toFixed(amount: string | number, decimals: number) {
  amount = amount.toString();
  const dotIndex = amount.indexOf('.');
  if (dotIndex === -1) return parseFloat(amount);
  if (amount.length - 1 - dotIndex > decimals) {
    return parseFloat(amount.substring(0, dotIndex + decimals + 1));
  }

  return parseFloat(amount);
}

export function toLocale(amount: string | number) {
  return typeof amount === 'string'
    ? parseFloat(amount).toLocaleString()
    : amount.toLocaleString();
}
