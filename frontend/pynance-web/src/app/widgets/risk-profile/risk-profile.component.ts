import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';
import { Component, Input, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { Holding } from 'src/app/models/holding';
import { LogService } from 'src/app/services/log.service';
import { PynanceService } from 'src/app/services/pynance.service';
import { containsObject } from 'src/utilities';
import { DomSanitizer } from '@angular/platform-browser';
import { MatTable } from '@angular/material/table';
import { Portfolio } from 'src/app/models/portfolio';


@Component({
  selector: 'app-risk-profile',
  templateUrl: './risk-profile.component.html'
})
export class RiskProfileComponent implements OnInit {
  private location : string = "app.widgets.risk-profile.RiskProfileComponent"
  public portfolio : Holding[] = [];
  public displayedColumns: string[] = [];
  public calculateDisabled :boolean = true;
  public clearDisabled : boolean = true;
  public loaded : boolean = false;
  public loading : boolean = false;
  public startDate : string = null;
  public endDate : string = null;
  public img: any = null

  @Input() 
  public explanationDisabled;
  
  @ViewChild('statisticsTable')
  private statisticsTable : MatTable<Holding[]>;
  
  constructor(private pynance : PynanceService,
              private sanitizer : DomSanitizer,
              private logs : LogService) { }

  ngOnInit(): void {
  }
  
  public calculate() : void{
    this.calculateDisabled = true;
    this.clearDisabled = false;
    this.loading = true;
    let imgLoaded = false;
    let jsonLoaded = false;
    this.pynance.riskProfileJPEG(this.getTickers(), this.getEndDate(), this.getStartDate())
                  .subscribe( (imgData) =>{
                    let imgUrl = URL.createObjectURL(imgData)
                    this.img = this.sanitizer.bypassSecurityTrustUrl(imgUrl);
                    imgLoaded = true;
                    if(jsonLoaded){
                      this.loading = false;
                      this.loaded = true;
                      this.displayedColumns=[ 'ticker', 'return', 'volatility', 'sharpe', 'beta']
                    };
                  });
    this.pynance.riskProfile(this.getTickers(), this.getEndDate(), this.getStartDate())
                  .subscribe( (profileData : Portfolio) => {
                    this.portfolio = profileData.holdings
                    jsonLoaded = true;
                    if(imgLoaded){
                      this.loading = false;
                      this.loaded = true;
                      this.displayedColumns=['ticker','return','volatility','sharpe','beta']
                    };
                  });

  }

  public clear() : void {
    this.calculateDisabled = true;
    this.clearDisabled = true;
    this.loaded = false;
    this.loading = false;
    this.portfolio = [];
    this.displayedColumns = [];
    this.statisticsTable.renderRows()
    this.img = null;
  }

  public removeHolding(holding : Holding) : void{
    let index = this.portfolio.indexOf(holding);
    this.portfolio.splice(index, 1);

    if(this.portfolio.length==0){
      this.clearDisabled=true;
      this.displayedColumns = [];
    }
    
    this.statisticsTable.renderRows()
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
      this.portfolio.push({ ticker: ticker, allocation: null, shares: null, 
                            annual_return: null, annual_volatility: null,
                            sharpe_ratio: null, asset_beta: null})
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
