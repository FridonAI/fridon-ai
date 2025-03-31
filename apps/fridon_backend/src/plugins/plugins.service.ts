import { Injectable } from '@nestjs/common';
import { Plugin, PluginsRepository } from './plugins.repository';
import { PrismaService } from 'nestjs-prisma';

@Injectable()
export class PluginsService {
  constructor(
    private readonly pluginRepository: PluginsRepository,
    private readonly prisma: PrismaService,
  ) {}

  setPlugins(plugins: Plugin[]): void {
    const orderedPlugins = [
      plugins.find((p) => p.name === 'Intelligent Coin Searcher'),
      plugins.find((p) => p.name === 'Coin Technical Analyzer'),
      plugins.find((p) => p.name === 'Emperor Trader'),
      plugins.find((p) => p.name === 'Solana Bonk Educator'),
      plugins.find((p) => p.name === 'Wallet'),
      plugins.find((p) => p.name === 'Coin Observer'),
    ].filter(Boolean);
    this.pluginRepository.set(orderedPlugins);
  }

  getPlugins(): Plugin[] {
    return this.pluginRepository.findAll();
  }

  get(slug: string): Plugin | undefined {
    const plugins = this.pluginRepository.findAll();
    return plugins.find((plugin) => plugin.slug === slug);
  }

  getDefaultPlugins(): Plugin[] {
    const defaultPluginSlugs = [
      'coin-technical-analyzer',
      'coin-technical-chart-searcher',
      'og-traders-simulator',
      'wallet',
      'solana-bonk-educator',
      'coin-observer',
    ];

    return this.pluginRepository
      .findAll()
      .filter((plugin) => defaultPluginSlugs.includes(plugin.slug));
  }

  getFreePlugins(): Plugin[] {
    return this.pluginRepository
      .findAll()
      .filter((plugin) => plugin.price === 0);
  }

  getPluginOwner(id: string): string {
    const plugin = this.get(id);
    if (!plugin) {
      throw new Error(`Plugin[${id}] not found`);
    }

    return plugin.owner;
  }

  async getSubscribersCount(pluginId: string): Promise<number> {
    const res = await this.prisma.walletPlugin.count({
      where: { pluginId },
    });

    return res;
  }
}
