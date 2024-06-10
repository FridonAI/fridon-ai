import { Injectable } from '@nestjs/common';

export type Plugin = {
  name: string;
  slug: string;
  imageUrl?: string | null;
  description: string;
  type: string;
  owner: string;
  examples: any[];
  functions: {
    name: string;
    description: string;
    examples: any[];
    parameters: string;
  }[];
  price: number;
};

@Injectable()
export class PluginsRepository {
  private plugins: Plugin[] = [];

  set(plugins: Plugin[]) {
    this.plugins = [...plugins];
  }

  findAll(): Plugin[] {
    return this.plugins;
  }
}
