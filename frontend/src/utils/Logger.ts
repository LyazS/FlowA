class Logger {
  private name: string

  constructor(name: string) {
    this.name = name
  }

  log(...data: any[]): void {
    console.log(`[${this.name}]`, ...data)
  }

  debug(...data: any[]): void {
    console.debug(`[${this.name}]`, ...data)
  }

  info(...data: any[]): void {
    console.info(`[${this.name}]`, ...data)
  }

  warn(...data: any[]): void {
    console.warn(`[${this.name}]`, ...data)
  }

  error(...data: any[]): void {
    console.error(`[${this.name}]`, ...data)
  }
}

export default Logger
