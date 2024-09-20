import { Injectable } from '@nestjs/common';
import Decimal from 'decimal.js';

@Injectable()
export class NumberFormatter {
  toUINumber(value: Decimal, decimals: number): string {
    return this.toCommaFormattedNumber(
      value
        .div(10 ** decimals)
        .toDecimalPlaces(decimals)
        .toString(),
    );
  }

  toPercent(value: number, decimalPlaces: number): string {
    return `${(value * 100).toFixed(decimalPlaces)}%`;
  }

  toFormattedPercent(value: Decimal | undefined): string {
    return value ? this.toPercent(value.toNumber(), 4) : '-';
  }

  toFormattedUsd(value: Decimal | undefined): string {
    return value ? `$${value.toDecimalPlaces(2).toString()}` : '-';
  }

  toNativeNumber(value: number | string, decimals: number): Decimal {
    return new Decimal(value)
      .toDecimalPlaces(decimals)
      .mul(10 ** decimals)
      .floor();
  }

  toCommaFormattedNumber(value: string): string {
    const [whole, fraction] = value.split('.');
    if (!whole) return value;
    const formattedWhole = [...whole]
      .reduce((acc, letter, index) => {
        if (index !== 0 && (whole.length - index) % 3 === 0) {
          acc.push(',');
        }
        acc.push(letter);
        return acc;
      }, [] as string[])
      .join('');

    if (fraction != null) {
      return `${formattedWhole}.${fraction}`;
    } else {
      return formattedWhole;
    }
  }
}
