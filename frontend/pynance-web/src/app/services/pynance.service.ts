import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { Portfolio } from '../models/portfolio';
import { LogService } from './log.service';
import {environment} from '../../environments/environment'

const ENDPOINTS ={
  optimize:{
    endpoint:'api/optimize',
    parameters:{
      tickers: 'tickers',
      startDate: 'start',
      endDate: 'end',
      targetReturn: 'target',
      investment: 'invest',
      sharpeRatio: 'sharpe'
    }
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
        query = query + `${ENDPOINTS.optimize.parameters.tickers}=${ticker}`;
        first = false;
      }
      else{
        query = query + `&${ENDPOINTS.optimize.parameters.tickers}=${ticker}`;
      }
    }
    return query;
  }

  public optimize(tickers: string[], endDate : string = null, startDate : string = null, 
                  targetReturn : number = null, investment : number = null,
                  method: boolean): Observable<Portfolio>{
    let baseUrl: string = `${environment.backendUrl}/${ENDPOINTS.optimize.endpoint}`;
    let query: string = this.formatQueryTickers(tickers)

    if (endDate){ query = query + `&${ENDPOINTS.optimize.parameters.endDate}=${endDate}`; }
    if(startDate){ query = query + `&${ENDPOINTS.optimize.parameters.startDate}=${startDate}`; }
    if(targetReturn){ query = query + `&${ENDPOINTS.optimize.parameters.targetReturn}=${targetReturn}`; }
    if(investment){ query = query + `&${ENDPOINTS.optimize.parameters.investment}=${investment}`}
    if(!method){ query = query + `&${ENDPOINTS.optimize.parameters.sharpeRatio}=true`}

    let queryUrl = baseUrl + "?" + query

    this.logs.log(`Querying backend at ${queryUrl}`, this.location)

    // may have to manually map response
    return this.http.get<Portfolio>(queryUrl)
      .pipe( 
        tap( response => {this.logs.log(`Received response from backend`, this.location); } ),
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
