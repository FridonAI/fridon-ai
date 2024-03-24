import { Inject } from '@nestjs/common';
import {
  BalanceType,
  SplTokenType,
  TokenListJsonType,
  TokenListType,
} from '../types';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { Position } from '@hubbleprotocol/kamino-lending-sdk';
import { NumberFormatter } from './number-formatter';
import { TokenBalance } from '../../providers/wallet-factory';

const STRICT_TOKEN_LIST_URL = 'https://token.jup.ag/strict';

export class BlockchainTools {
  constructor(
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
    private numberFormatter: NumberFormatter,
  ) {}

  async fetchTokenList(): Promise<TokenListType> {
    const data = await fetch(STRICT_TOKEN_LIST_URL);
    const tokenListJson: TokenListJsonType[] = await data.json();

    const tokenList: TokenListType = tokenListJson.map((token) => {
      return {
        mintAddress: token.address,
        decimals: token.decimals,
        name: token.name,
        symbol: token.symbol,
      } as SplTokenType;
    });

    return tokenList;
  }

  async getMintAddresses(): Promise<string[]> {
    const cachedTokenList: TokenListType | undefined =
      await this.cacheManager.get('tokenList');

    const strictTokenList = cachedTokenList || (await this.fetchTokenList());

    return strictTokenList.map((token) => token.mintAddress);
  }

  async convertSymbolToMintAddress(symbol: string): Promise<string> {
    const cachedTokenList: TokenListType | undefined =
      await this.cacheManager.get('tokenList');

    const strictTokenList = cachedTokenList || (await this.fetchTokenList());

    const token = strictTokenList.find(
      (token) => token.symbol.toLowerCase() === symbol.toLowerCase(),
    );

    if (!token) {
      throw new Error(`Token with symbol ${symbol} not found`);
    }
    return token.mintAddress;
  }

  async convertMintAddressToSymbol(mintAddress: string): Promise<string> {
    const cachedTokenList: TokenListType | undefined =
      await this.cacheManager.get('tokenList');

    const strictTokenList = cachedTokenList || (await this.fetchTokenList());

    const token = strictTokenList.find(
      (token) => token.mintAddress === mintAddress,
    );

    if (!token) {
      throw new Error(`Token with mint address ${mintAddress} not found`);
    }
    return token.symbol;
  }

  async findTokenByMintAddress(mintAddress: string): Promise<SplTokenType> {
    const cachedTokenList: TokenListType | undefined =
      await this.cacheManager.get('tokenList');

    const strictTokenList = cachedTokenList || (await this.fetchTokenList());

    const token = strictTokenList.find(
      (token) => token.mintAddress === mintAddress,
    );

    if (!token) {
      throw new Error(`Token with mint address ${mintAddress} not found`);
    }
    return token;
  }

  async convertPositionToBalance(position: Position): Promise<BalanceType> {
    const mintAddress = position.mintAddress.toBase58();
    const token = await this.findTokenByMintAddress(mintAddress);
    return {
      symbol: token.symbol,
      mintAddress,
      amount: this.numberFormatter.toUINumber(position.amount, token.decimals),
    };
  }

  async convertTokenBalanceToBalance(
    token: TokenBalance,
  ): Promise<BalanceType> {
    const symbol = await this.convertMintAddressToSymbol(token.mint);
    return {
      symbol: symbol,
      mintAddress: token.mint,
      amount: token.amount,
    };
  }

  async convertTokenBalancesToBalances(
    tokens: TokenBalance[],
  ): Promise<BalanceType[]> {
    return Promise.all(
      tokens.map((token) => this.convertTokenBalanceToBalance(token)),
    );
  }

  async convertPositionsToBalances(
    positions: Position[],
  ): Promise<BalanceType[]> {
    return Promise.all(
      positions.map((position) => this.convertPositionToBalance(position)),
    );
  }
}
