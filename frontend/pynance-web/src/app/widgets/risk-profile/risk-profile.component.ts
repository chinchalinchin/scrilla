import { Component, Input, OnInit } from '@angular/core';
import { Holding } from 'src/app/models/holding';
import { LogService } from 'src/app/services/log.service';
import { PynanceService } from 'src/app/services/pynance.service';
import { containsObject } from 'src/utilities';

@Component({
  selector: 'app-risk-profile',
  templateUrl: './risk-profile.component.html'
})
export class RiskProfileComponent implements OnInit {
  private location : string = "app.widgets.risk-profile.RiskProfileComponent"
  public portfolio : Holding[] = [];
  public calculateDisabled = true;
  public clearDisabled = true;
  public startDate : string = null;
  public endDate : string = null;

  @Input() 
  public explanationDisabled;
  
  constructor(private pynance : PynanceService,
              private logs : LogService) { }

  ngOnInit(): void {
  }
  
  public calculate() : void{

    this.calculateDisabled = true;
  }

  public clear() : void {

    this.calculateDisabled = true;
    this.clearDisabled = true;
  }

  public getTickers() : string[]{
    let tickers : string [] = []
    for(let holding of this.portfolio){
      tickers.push(holding.ticker)
    }
    return tickers;
  }

  public setTickers(inputTickers : string[]){
    this.logs.log(`received tickers: ${inputTickers}`, this.location)

    let unduplicatedTickers : string[] = [];
    let portfolioTickers : string[] = this.getTickers();
    
    for(let ticker of inputTickers){
      if(!containsObject(ticker, portfolioTickers)){ unduplicatedTickers.push(ticker); }
    }

    for(let ticker of unduplicatedTickers){
      this.portfolio.push({ ticker: ticker, allocation: null, shares: null, annual_return: null, annual_volatility: null})
    }

    this.calculateDisabled = false;
    this.clearDisabled = false;
  }

  public setDates(inputDates: string[]) : void {
    this.logs.log(`Received dates ${inputDates}`, this.location)
    this.startDate = inputDates[0]
    this.endDate = inputDates[1]
  }

  public getStartDate() : string { return this.startDate; }

  public getEndDate() : string { return this.endDate; }
}
