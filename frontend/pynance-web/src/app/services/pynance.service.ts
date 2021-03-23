import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { Portfolio } from '../models/portfolio';
import { LogService } from './log.service';
import {environment} from '../../environments/environment'
import { Holding } from '../models/holding';

const ENDPOINTS ={
  optimize:'api/optimize',
  riskprofile:'api/risk-return',
  parameters:{
    tickers: 'tickers',
    startDate: 'start',
    endDate: 'end',
    targetReturn: 'target',
    investment: 'invest',
    sharpeRatio: 'sharpe',
    jpeg : 'jpeg'
  }
}

@Injectable({
  providedIn: 'root'
})
export class PynanceService {
  private location : string = "app.services.pynance";

  constructor(private logs: LogService,
              private http: HttpClient) { }


  public formatQueryTickers(tickers: string[]) : string{
    let query: string = "";
    let first: boolean = true;
    for(let ticker of tickers){
      if (first){
        query = query.concat(`${ENDPOINTS.parameters.tickers}=${ticker}`);
        first = false;
      }
      else{
        query = query.concat(`&${ENDPOINTS.parameters.tickers}=${ticker}`);
      }
    }
    return query;
  }

  public formatSecondaryArguments(endDate : string = null, startDate: string = null,
                                  targetReturn : number = null, investment : number = null,
                                  method: boolean = false, jpeg : boolean = false): string {
    let query : string = ""
    if (endDate){ query = query.concat(`&${ENDPOINTS.parameters.endDate}=${endDate}`); }
    if(startDate){ query = query.concat(`&${ENDPOINTS.parameters.startDate}=${startDate}`); }
    if(targetReturn){ query = query.concat(`&${ENDPOINTS.parameters.targetReturn}=${targetReturn}`); }
    if(investment){ query = query.concat(`&${ENDPOINTS.parameters.investment}=${investment}`); }
    if(method){ query = query.concat(`&${ENDPOINTS.parameters.sharpeRatio}=true`)}
    if(jpeg){ query = query.concat(`&${ENDPOINTS.parameters.jpeg}=true`); }
    return query;
  }

  public getRiskProfileUrl(tickers : string [], endDate : string = null, startDate  : string = null,
                            jpeg : boolean = false) : string{
    let baseUrl : string = `${environment.backendUrl}/${ENDPOINTS.riskprofile}`;
    let query : string = this.formatQueryTickers(tickers);
    let queryArgs : string = this.formatSecondaryArguments(endDate, startDate, null, null, false, jpeg);
    let queryUrl : string = baseUrl.concat("?", query, queryArgs);
    return queryUrl;
  }

  public riskProfile(tickers : string[], endDate : string = null, 
                      startDate : string = null) : Observable<Portfolio> {
    let queryUrl = this.getRiskProfileUrl(tickers, endDate, startDate);
    this.logs.log(`Querying backend at ${queryUrl}`, this.location)
    return this.http.get<Portfolio>(queryUrl)
                .pipe(
                  tap( _ => {this.logs.log(`Received response from backend risk profile endpoint`, this.location)}),
                  catchError(this.handleError<Portfolio>('riskProfile', null))
                );
  }

  public riskProfileJPEG(tickers: string[], endDate : string = null, 
                          startDate : string = null) : Observable<Blob>{
      let queryUrl = this.getRiskProfileUrl(tickers, endDate, startDate, true);
      this.logs.log(`Querying backend at ${queryUrl}`, this.location);
      return this.http.get(queryUrl, 
                          { headers: new HttpHeaders({'Content-Type': 'img/png'}), observe: 'body', responseType: 'blob'})
                  .pipe(
                    tap( _ => {this.logs.log(`Received response from backend risk profile endpoint`, this.location)}),
                    catchError(this.handleError<Blob>('riskProfile', null))
                  );
  }

  public optimize(tickers: string[], endDate : string = null, startDate : string = null, 
                  targetReturn : number = null, investment : number = null,
                  method: boolean = true): Observable<Portfolio>{
    let baseUrl : string = `${environment.backendUrl}/${ENDPOINTS.optimize}`;
    let query : string = this.formatQueryTickers(tickers); 
    let queryArgs : string = this.formatSecondaryArguments(endDate, startDate, targetReturn, investment, method);
    let queryUrl : string = baseUrl.concat("?", query, queryArgs);

    this.logs.log(`Querying backend at ${queryUrl}`, this.location);

    // may have to manually map response
    return this.http.get<Portfolio>(queryUrl)
              .pipe( 
                tap( _ => {this.logs.log(`Received response from backend optimize endpoint`, this.location); } ),
                catchError(this.handleError<Portfolio>('optimize', null))
            );
  }


/**
 * Handle Http operation that failed.
 * Let the app continue.
 * @param operation - name of the operation that failed
 * @param result - optional value to return as the observable result
 */
private handleError<T>(operation = 'operation', result?: T) {
  return (error: any): Observable<T> => {

    // TODO: better job of transforming error for user consumption
    this.logs.log(`${operation} failed: ${error.message}`, this.location);

    // Let the app keep running by returning an empty result.
    return of(result as T);
  };
}
}
