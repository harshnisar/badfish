# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2016 Harsh Nisar and Deshana Desai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pandas as pd
import seaborn as sns
import numpy as np
from scipy import stats
from collections import OrderedDict
from .plotting import plot as bfplot

class MissFrame:
    '''
    Returns a the same frame, but with 1 where the data is missing and 0 where its not.
    
    Parameters:
    ----------
    df: Pandas DataFrame, required.
        The DataFrame which needs to be analysed for missing values.

    missing_codes: list, optional
        List of codes used to represent missingness in the dataset.
        Eg. "missing", "n/a", "Didn't enter" and so on.
        Codes will be replaced by NaN and treated as missing internally.
        Warning: Each and every instance of a missing code will be replaced
        by NaN. Make sure all of them are supposed to be treated as missing
        and aren't valid data.

    Attributes:
    ----------
    data: Pandas DataFrame, The original data.

    miss_frame: Pandas DataFrame, Boolean mask wherever data is missing. 


    Examples
    --------
    >>> df = pd.read_csv('demo.csv')
    >>> mf = bf.MissFrame(df)
    '''
    
    plot = bfplot



    def __init__(self, df, missing_codes):
        # May not need to copy
        self.data =  df.copy()

        if missing_codes: #if list not empty
            for code in missing_codes:
                df = df.replace(code, np.nan)

        self.miss_frame = df.isnull()

    
    def _masked_missframe(self, where, how, columns):
        """
        Returns a subset of missframe based on conditions.

        Parameters:
        -----------
        where: list of columns
            Select subset of the DataFrame to work on where specified columns 
            are missing. If None, entire DataFrame is considered.

        how: {'all'|'any'} 
            Whether all or any of the columns specified in where clause should
            be missing.

        columns: list of columns
            Columns the final data should retain.

        """



        if columns == None:
            columns = self.miss_frame.columns

        if where != None:
            if how == 'all':
                return self.miss_frame[columns].loc[self.miss_frame[where].all(axis = 1)]
            else:
                return self.miss_frame[columns].loc[self.miss_frame[where].any(axis = 1)]
        else:
            return self.miss_frame[columns]


    def counts(self, columns = None, where = None, how = 'all', norm = False, ascending = False):
        """ 
        Returns the count of missing values per column.

        Parameters:
        -----------
        where: list of columns
            Select subset of the DataFrame to work on where specified columns 
            are already missing. If None, entire DataFrame is considered.

        how: {'all'|'any'} 
            Whether all or any of the columns specified in where clause should
            be missing.

        columns: list of columns
            Columns the final data should retain.

        Returns:
        -------
        mf_sum : DataFrame
            Count of missing values for each column.

        """

        mf_ = self._masked_missframe(where = where, columns = columns, how = how)

        mf_sum = mf_.sum()
        
        if norm == True:
            #TODO: Not sure which counts should come here. mf_ or miss_frame
            mf_sum_normed = mf_sum/mf_.count()
            mf_sum_normed.sort_values(ascending=ascending, inplace=True)
            return mf_sum_normed
        else:
            mf_sum.sort_values(ascending=ascending, inplace=True)
            return mf_sum


    def corr(self, where = None, columns = None, how = 'all'):
        """ 
        Correlation between columns based on boolean representing whether value is
        missing or not. High correlation could represent values missing or being present
        at the same time. 

        Parameters:
        -----------
        where: list of columns
            Select subset of the DataFrame to work on where specified columns 
            are already missing. If None, entire DataFrame is considered.

        how: {'all'|'any'} 
            Whether all or any of the columns specified in where clause should
            be missing.

        columns: list of columns
            Columns the final DataFrame should retain.

        Returns:
        -------
        corr_ : DataFrame
            Correlation matrix
        
        """
        
        mf_ = self._masked_missframe(where = where, columns = columns, how = how)
        corr_ = mf_.corr()

        #Drop columns which have all values NaN. No value was missing.
        corr_ = corr_.dropna(axis = 1, how = 'all')

        return corr_

    def pattern(self, where = None, columns = None, how ='any', norm = True, threshold = 0.10, ascending = False):
        """
        Shows the frequency of possible patterns of missing and non-missing values.
        
        Use mf.plot to see the same table visualized. Plot is inspired by VIM package in R.
        True represents Missing and False represent data being present.

        Parameters:
        -----------
        where: list of columns
            Select subset of the DataFrame to work on where specified columns 
            are already missing. If None, entire DataFrame is considered.

        how: {'all'|'any'} 
            Whether all or any of the columns specified in where clause should
            be missing.

        columns: list of columns
            Columns the final DataFrame should retain.

        norm: bool, default True
            Whether frequency should be normed. Normalized by count of rows in final
            DataFrame after masking by where clause.

        threshold: float or int, default 0.10
            Only show patterns whose frequency passes a certain threshold.

        
        Returns:
        -------
        pat_ : DataFrame
            Counts for different combinations of missing data. 
        
        """

        mf_ = self._masked_missframe(where = where, columns = columns, how = how)
        

        pat_ = mf_.groupby(mf_.columns.tolist()).size()
        pat_ = pat_.sort_values(ascending = ascending)


        # Didn't like this part. Added code just because module.
        if (norm == True):
            if(threshold < 1):
                pat_ = pat_/ pat_.sum()
                pat_ = pat_.loc[pat_> threshold]
            else:
                pat_ = pat_.loc[pat_> threshold]
                pat_ = pat_/ pat_.sum()
        else:
            if(threshold < 1):
                pat_ = pat_.loc[pat_/pat_.sum()> threshold]    
            else:
                pat_ = pat_.loc[pat_> threshold]    

        
        pat_ = pat_.reset_index()
        return pat_ 
   

    def cohort(self, group, columns = None, how='any'):
        """
        Tries to find signigicant group differences between values of
        columns other than the ones specified in the group clause. Group
        made on the basis of missing or non-missing of columns in the group clause.

        Parameters:
        -----------
        group: list of columns
            Columns on the basis of which groups will be made.

        how: {'all'|'any'} 
            Whether all or any of the columns specified in group clause should
            be missing.

        columns: list of columns
            Columns the final DataFrame should retain.

        Returns:
        -------
        out : DataFrame
            Generated statistics for the group differences.
        """

        #TODO: Add warning class about the useful ness of this test. 

        if how == 'all':
            group_ = self.miss_frame[group].all(axis = 1)
        if how == 'any':
            group_ = self.miss_frame[group].any(axis = 1)

        if columns == None:
            columns = self.data.columns

        order_col =  ['Column', 
            'Non-null values in Group (missing)',
            'Non-null values in Group (non-missing)',
            'Mean - Group (missing)', 
            'Mean - Group (non-missing)',
            'T (Equal Variance)',
            'p value (Equal Variance)',
            'T (Unequal Variance)', 
            'p value (Unequal Variance)'
            ]
        
        results_list = []

        for col in columns:

            if self.data[col].dtype != np.number:
                "Skipping {0} because not a number".format(col)
                continue
            
            missing = self.data[col].loc[group_]
            nonmissing = self.data[col].loc[~group_]

            results = {}            
            results['Column'] = col
            results['Non-null values in Group (missing)'] =  missing.dropna().shape[0]
            results['Non-null values in Group (non-missing)'] = nonmissing.dropna().shape[0]
            
            results['Mean - Group (missing)'] = missing.mean()
            results['Mean - Group (non-missing)'] =  nonmissing.mean()

            two_sample = stats.ttest_ind(missing, nonmissing, nan_policy = 'omit',axis = 0)
            
            results['T (Equal Variance)'] = two_sample[0]
            results['p value (Equal Variance)'] = two_sample[1]


            two_sample_diff_var = stats.ttest_ind(missing, nonmissing, nan_policy = 'omit',equal_var=False)
            results['T (Unequal Variance)'] = two_sample_diff_var[0]
            results['p value (Unequal Variance)'] = two_sample_diff_var[1]


            results_list.append(results)


        out = pd.DataFrame(results_list)[order_col]
        return out

    def frequency_item_set(self, columns = None, support = 0.1, rules = False, confidence = 0.8, engine = 'pymining'):
        """
        Use frequency item set mining to find subgroups where data goes 
        missing together.
        
        Parameters:
        ----------
        columns: list, default None
            Subset of the columns you want to use.
        
        support: float, default 0.1
            Minimum support to use while item set mining. Too small values can break memory.
            Support should be greater than zero and less than 1.

        rules: bool, default True
            Whether association rules should be mined. If True, method returns two_sample
            dataframes instead of one.

        confidence: float, default
            Minimum confidence for rules being mined. Should be between 0 and 1.

        engine: {'pymining'}
            Only one engine is being supported right now.
        
       
        Returns:
        -------
        item_sets_df, rules_df : DataFrame, DataFrame
            Tabulated results for itemsets and association rules mined. 
            
        """ 

        from pymining import itemmining, assocrules

        if support<=0 or support>1: #support should be between one and zero.
            print('Support has to be between 0 and 1')
            return

        if confidence<0 or confidence>1: #confidence can be zero.
            print('Confidence has to be between 0 and 1')
            return
            


        mf_ = self._masked_missframe(where = None, columns = columns, how = 'any')
        
        # Converting all missing values to 1, and non-missing to nan.
        bench = pd.DataFrame(np.where(mf_, 1, np.nan), columns = mf_.columns)

        # Replacing 1's with the index of the column they belong to.
        # Converting to numbers instead of column names for supposed performance boost.
        bench = bench * list(range(0, mf_.columns.shape[0]))

        rows = bench.values
        transactions = []
        for row in rows:
            # Removing the nans in each row and compressing the rows.
            # (nan, 1, nan, 3) --> (1, 3)
            transactions.append(tuple(row[~np.isnan(row)]))

        # Converting float threshold to represent number of rows.
        support = int(support*mf_.shape[0])

        relim_input = itemmining.get_relim_input(transactions)
        item_sets = itemmining.relim(relim_input, min_support=support)
        
        # Converting to DataFrames and getting columns names back.
        item_sets_df = pd.DataFrame({'Itemset':list(item_sets.keys()), 'Support': list(item_sets.values())})
        item_sets_df.Itemset = item_sets_df.Itemset.apply(lambda x: mf_.columns[list(x)].tolist())

        
        # For now the same supports being used in FIM and Association Rules.
        rules = assocrules.mine_assoc_rules(item_sets, min_support=support, min_confidence=confidence)

        rules_df = pd.DataFrame(rules, columns = ['X =>', 'Y', 'Support', 'Confidence'])
        # Converting rules to DataFrame and getting columns names back.
        rules_df['X =>'] = rules_df['X =>'].apply(lambda x: mf_.columns[list(x)].tolist())
        rules_df['Y'] = rules_df['Y'].apply(lambda x: mf_.columns[list(x)].tolist())
        
        return item_sets_df, rules_df


    def get_best_column_set(self):
        """
        Tabulates best possible cost to include each column.
        some columns having missing values spread accross the dataframe randomly,
        whereas some have isolated missing values. 
        Adding a column with missing values affects list wise deletion of DataFrame.
        Depends on the columns already existing in the DataFrame.        
        """
        return NotImplemented

