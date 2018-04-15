#include "predict.h"
#include <stdio.h>
#include "predict.h"
#include <stdio.h>
#include <vector>
#include <string>
#include <algorithm>
#include <string.h>
#include <random>
#include <math.h>


using namespace std;
 
int predict_time_diff(string begin,string end){
	if(atoi(begin.substr(5,7).c_str())==atoi(end.substr(5,7).c_str()))
		return atoi(end.substr(8,10).c_str())- atoi(begin.substr(8,10).c_str());
	else 
		return atoi(end.substr(8,10).c_str())- atoi(begin.substr(8,10).c_str())+30;
}

int time2min(const string& time) {
	return 60 * (10 * (time[0] - '0') + time[1] - '0') + 10 * (time[3] - '0') + time[4] - '0';
}

int flavor2num(string flavor_name){
	int begin,end;
	begin=flavor_name.find_last_of('r')+1;
	end=flavor_name.length();
	return atoi(flavor_name.substr(begin,end).c_str());
}

vector<string> cstr2words(const char* line_ptr){
	vector<string> words;
	string tem;
	while(*line_ptr!='\n'){
		if(*line_ptr!=' '&&*line_ptr!='\t')
			tem.push_back(*line_ptr);
		else if(tem!=""){
			words.push_back(tem);
			tem="";
		}
		++line_ptr;
	}
	if(tem!="")
		words.push_back(tem);
	return words;
}	


//你要完成的功能总入口
void predict_server(char * info[MAX_INFO_NUM], char * data[MAX_DATA_NUM], int data_num, char * filename)
{
	
	//解析input输入文件参数
	int phsM_cpu_num=0,phsM_Mem_size=0;
	int flavortypes_num=0;
	vector<flavortype> flavors;
	string opt_pram,time_begin,time_end;
	unsigned int time_diff=0;
	 
	for(int i=0;info[i]!=NULL;++i){
		if(i==0){//物理服务器参数解析
			vector<string> s;
			s=cstr2words(info[i]);
			phsM_cpu_num=atoi(s[0].c_str());
			phsM_Mem_size=atoi(s[1].c_str());
		}
		if(i==2){//预测虚拟机类型数目
			vector<string> s;
			s=cstr2words(info[i]);
			flavortypes_num=atoi(s[0].c_str());
		}
		if(i==3){//预测虚拟机具体类型及参数vector
			for(int j=0;j<flavortypes_num;++j){
				flavortype tem;
				vector<string> s;
				s=cstr2words(info[i+j]);
				tem.name=s[0];
				tem.cpu_num=atoi(s[1].c_str());
				tem.Mem_size=atoi(s[2].c_str())/1024;
				tem.predict_num=0;
				flavors.push_back(tem);
			}
		}
		if(i==(flavortypes_num+4)){//物理服务器优化参数解析
			vector<string> s;
			s=s=cstr2words(info[i]);
			opt_pram=s[0];
		}
		if(i==(flavortypes_num+6)){//预测开始时间解析
			vector<string> s;
			s=s=cstr2words(info[i]);
			time_begin=s[0];
		}
		if(i==(flavortypes_num+7)){//预测结束时间解析
			vector<string> s;
			s=cstr2words(info[i]);
			time_end=s[0];
		}
	}
	
	time_diff=predict_time_diff(time_begin,time_end);//解析预测时间间隔

	//解析历史虚拟机请求数据traindata
	vector<dataIterm> Data;
	for(int i=0;i<data_num;++i){
		dataIterm Iterm;
		vector<string> s;
		s=cstr2words(data[i]);
		Iterm.id=s[0];
		Iterm.flavor=s[1];
		Iterm.date=s[2];
		Iterm.time=s[3];
		Data.push_back(Iterm);
	}
	
	vector<dateData> date_Data;
	dateData date_data_tem;
	//初始化date_Data的date参数和flavortimelist参数
	for(unsigned int i=0;i<Data.size();++i){
		int flavornum=flavor2num(Data[i].flavor);
		if(i==0)
			date_data_tem=dateData(Data[i].date);
		if(flavornum<flavortypes_num)
			date_data_tem.flavortimelist[flavornum-1].push_back(Data[i].time);
		
		if((i+1)==Data.size()||Data[i]!=Data[i+1])
		{
			date_Data.push_back(date_data_tem);
			if((i+1)!=Data.size())
				date_data_tem=dateData(Data[i+1].date);
		}
	}
	
	//初始化date_Data的flavornumlist参数
	for(unsigned int i=0;i<date_Data.size();++i){
		for(unsigned int j=0;j<date_Data[i].flavortimelist.size();++j){
			int count=0;
			for(unsigned int k=0;k<date_Data[i].flavortimelist[j].size();++k){
				++count;
				if((k+1)==date_Data[i].flavortimelist[j].size()||time2min(date_Data[i].flavortimelist[j][k+1])-time2min(date_Data[i].flavortimelist[j][k])>1)
				{
					date_Data[i].flavornumlist[j].push_back(count);
					count=0;
				}
			}
		}
		for(unsigned int j=0;j<date_Data[i].flavortimelist.size();++j){
			sort(date_Data[i].flavornumlist[j].begin(),date_Data[i].flavornumlist[j].end());
		}
	}
	
	//统计一天中各种订单的数量
	for (unsigned int i = 0; i < date_Data.size(); ++i) {
		for (unsigned int j = 0; j < date_Data[i].flavornumlist.size(); ++j) {
			int count_small = 0, count_mid = 0, count_large = 0, count_vlarge = 0;
			for (unsigned int k = 0; k < date_Data[i].flavornumlist[j].size(); ++k) {
				if (date_Data[i].flavornumlist[j][k] >= 1 && date_Data[i].flavornumlist[j][k] < 3)
					count_small=count_small+ date_Data[i].flavornumlist[j][k];
				if (date_Data[i].flavornumlist[j][k] >= 3 && date_Data[i].flavornumlist[j][k] < 9)
					count_mid=count_mid+ date_Data[i].flavornumlist[j][k];
				if (date_Data[i].flavornumlist[j][k] >= 9 && date_Data[i].flavornumlist[j][k] < 15)
					count_large=count_large+ date_Data[i].flavornumlist[j][k];
				if (date_Data[i].flavornumlist[j][k] >= 15)
					count_vlarge=count_vlarge+ date_Data[i].flavornumlist[j][k];
			}
			if (count_small!=0&&count_mid > 8 * count_small)
				count_mid = 0.5*count_mid;
			if (count_small != 0 && count_large > 15 * count_small)
				count_large = 0.5*count_large;
			if (count_small != 0 && count_mid > 20 * count_small)
				count_vlarge = 0.5*count_vlarge;
			date_Data[i].small_size.push_back(count_small);
			date_Data[i].mid_size.push_back(count_mid);
			date_Data[i].large_size.push_back(count_large);
			date_Data[i].vlarge_size.push_back(count_vlarge);
		}
	}

	reverse(date_Data.begin(), date_Data.end());//翻转历史虚拟机请求数据
	vector<sample> train_set;
	train_set.resize(SAMPLE_NUM);
	for (unsigned int k = 0; k < SAMPLE_NUM; ++k) {

		vector<vector<double> > data_cycle_small(MAX_CYCLE, vector<double>(MAX_FLAVOR_NUM, 0));
		vector<vector<double> > data_cycle_mid(MAX_CYCLE, vector<double>(MAX_FLAVOR_NUM, 0));
		vector<vector<double> > data_cycle_large(MAX_CYCLE, vector<double>(MAX_FLAVOR_NUM, 0));
		vector<vector<double> > data_cycle_vlarge(MAX_CYCLE, vector<double>(MAX_FLAVOR_NUM, 0));
		vector<vector<double> > data_cycle_sum(MAX_CYCLE, vector<double>(MAX_FLAVOR_NUM, 0));

		for (unsigned int i = 0, cycle = 0; i < date_Data.size() && cycle < MAX_CYCLE; ++i) {
			for (unsigned int j = 0; j < date_Data[i + k].small_size.size(); ++j) {
				if (j == 0||j==(MAX_FLAVOR_NUM-1) ){
					data_cycle_small[cycle][j] = data_cycle_small[cycle][j] + date_Data[i + k].small_size[j];	 
				}
				else {
					data_cycle_small[cycle][j] = data_cycle_small[cycle][j] + date_Data[i + k].small_size[j]-0.1*date_Data[i + k].small_size[j-1]-0.1*date_Data[i + k].small_size[j+1];
				}
				data_cycle_mid[cycle][j] = data_cycle_mid[cycle][j] + date_Data[i + k].mid_size[j];
				data_cycle_large[cycle][j] = data_cycle_large[cycle][j] + date_Data[i + k].large_size[j];
				data_cycle_vlarge[cycle][j] = data_cycle_vlarge[cycle][j] + date_Data[i + k].vlarge_size[j];
				data_cycle_sum[cycle][j] = data_cycle_small[cycle][j] + 0.6*data_cycle_mid[cycle][j] + 0.3*data_cycle_large[cycle][j] + 0.1*data_cycle_vlarge[cycle][j];
			}
			if ((i + 1) % time_diff == 0) {
				++cycle;
			}
		}
		train_set[k].data.resize(MAX_CYCLE);
		for (unsigned int j = 0; j < MAX_CYCLE; ++j) {
			train_set[k].data[j].resize(MAX_FLAVOR_NUM);
			train_set[k].data[j] = data_cycle_sum[j];
		}
	}
	//根据不同的订单详情分别预测
	 
	vector<double> predict_num(MAX_FLAVOR_NUM,0);
	int predict_sum=0;
	double W = 0;

	for (unsigned int j = 0; j<MAX_FLAVOR_NUM; ++j) {
		for (unsigned int cycle = 0; cycle<MAX_CYCLE; ++cycle) {
			switch (cycle) {
				case 0: {W = 0.75; break; }
				case 1: {W = 0.2; break; }
				case 2: {W = 0.05; break; }
				default: {W = 0; break; }
			}
			predict_num[j] = predict_num[j]+W*train_set[0].data[cycle][j];
		}
	}
	
	for(unsigned int i=0;i<flavors.size();++i){
		flavors[i].predict_num=predict_num[flavor2num(flavors[i].name)-1];
		predict_sum=predict_sum+flavors[i].predict_num;
	}
	
	vector<hostM> host_out;
	vector<flavortype> flavors_tem;
	vector<flavortype>::reverse_iterator iter_start,iter_first,iter_second;
	double delta1=0,delta2=0;
	hostM host_tem,host_first,host_second;
	flavors_tem=flavors;
	while(1){
		host_tem=hostM(phsM_cpu_num,phsM_Mem_size);
		for(iter_start=flavors.rbegin();iter_start!=flavors.rend();++iter_start){
			if((*iter_start).predict_num!=0){
				host_tem=hostM(phsM_cpu_num,phsM_Mem_size);
				--(*iter_start).predict_num;
				host_tem.vmflavor[flavor2num((*iter_start).name)-1]=host_tem.vmflavor[flavor2num((*iter_start).name)-1]+1;
				host_tem.rcpu_num=host_tem.rcpu_num-(*iter_start).cpu_num;
				host_tem.rMem_size=host_tem.rMem_size-(*iter_start).Mem_size;
				host_first=host_tem;
				host_second=host_tem;
				break;
			}
		}
		if(iter_start==flavors.rend())
			break;
		while(1){
			for(iter_first=iter_start;iter_first!=flavors.rend();++iter_first){
				if((*iter_first).predict_num!=0){
					host_first.vmflavor[flavor2num((*iter_first).name)-1]=host_first.vmflavor[flavor2num((*iter_first).name)-1]+1;
					host_first.rcpu_num=host_first.rcpu_num-(*iter_first).cpu_num;
					host_first.rMem_size=host_first.rMem_size-(*iter_first).Mem_size;
					if(host_first.rcpu_num<0||host_first.rMem_size<0){
						host_first=host_tem;
						continue;
					}else{
						delta1=fabs(host_first.rcpu_num/host_first.rMem_size-phsM_cpu_num/phsM_Mem_size);
						break;	
					}
				}	
			}
			if(iter_first==flavors.rend()){
				host_out.push_back(host_tem);
				break;
			}	
			for(iter_second=iter_first+1;iter_second!=flavors.rend();++iter_second){
				if((*iter_second).predict_num!=0){
					host_second.vmflavor[flavor2num((*iter_second).name)-1]=host_second.vmflavor[flavor2num((*iter_second).name)-1]+1;
					host_second.rcpu_num=host_second.rcpu_num-(*iter_second).cpu_num;
					host_second.rMem_size=host_second.rMem_size-(*iter_second).Mem_size;
					delta2=fabs(host_second.rcpu_num/host_second.rMem_size-phsM_cpu_num/phsM_Mem_size);
					break;
				}
			}
			if(iter_second!=flavors.rend()){
				if(delta1<=delta2){
					host_tem=host_first;
					host_second=host_tem;
					--(*iter_first).predict_num;
				}else{
					host_tem=host_second;
					host_first=host_tem;
					--(*iter_second).predict_num;
				}
			}else{
				host_tem=host_first;
				--(*iter_first).predict_num;
			}
			continue;	 
		}			
	}
	// 需要输出的内容
	char * result_file = (char *)"17\n\n0 8 0 20";
	int length=0;
	char buff[55000];

	flavors = flavors_tem;
	buff[0]=0;

	length = strlen(buff);
	sprintf(buff+length, "%d\n", predict_sum);
	for (unsigned int i = 0; i < flavors.size(); ++i) { 
		length = strlen(buff);
		sprintf(buff+length, "%s %d\n", &flavors[i].name[0],flavors[i].predict_num);
	}
	length = strlen(buff);
	sprintf(buff+length, "\n%zu\n", host_out.size());
	for (unsigned int i = 0; i < host_out.size(); ++i) {
		length = strlen(buff);
		sprintf(buff+length, "%d ", i+1);
		for (unsigned int j = 0; j < host_out[i].vmflavor.size(); ++j) {
			if (host_out[i].vmflavor[j] != 0) {
				length = strlen(buff);
				sprintf(buff + length, "flavor%d %d ", j + 1,host_out[i].vmflavor[j]);
			}	
		}
		length = strlen(buff);
		sprintf(buff + length, "\n");
	}
	
	result_file=buff;
	// 直接调用输出文件的方法输出到指定文件中(ps请注意格式的正确性，如果有解，第一行只有一个数据；第二行为空；第三行开始才是具体的数据，数据之间用一个空格分隔开)
	write_result(result_file, filename);
}
 