# CRM系统

## 一、简介

​	本系统一开始主要用于员工和客户信息的管理，随着业务的扩展和公司规模的扩大，后期逐渐添加了绩效考核、考勤等功能



## 二、主要功能

- 客户批量导入
- 为顾问自动分配订单，并发送通知
- 每日定时筛选超时客户，置为公共资源
- 顾问手动抢单
- 保存顾问和客户的历史关系
- 保存上课记录
- 员工考勤
- 使用Highcharts图表展示员工绩效
- 权限管理（组件）
- 记录的搜索和组合搜索
- 其他功能




## 三、功能详细

### 客户批量导入

​	用户需下载模板xlsx文件，按规定格式填写文档后，可实现客户信息的批量录入。

### 为顾问自动分配订单，并发送通知

​	1、根据顾问能力的大小，分配不同的权重和最大客户数量，在单个添加或批量录入客户信息后，基于Redis按既定规则匹配顾问，自动接收订单；

​	2、为顾问分配订单后，发送邮件、短信、微信等通知，通知方式可在配置文件中更改。

### 每日定时筛选超时客户，置为公共资源

​	顾问在跟进客户时，需要对每一次跟进创建记录，对于3天未跟进或15天未成单的客户，系统会在每日的凌晨2点利用crontab执行任务进行筛选，并将其置为公共资源。在此之前，每个顾问的客户只可由自己跟进，其他人不可查看。

### 顾问手动抢单

​	超时客户置为公共资源后，最后一个对其进行跟进的顾问不能进行抢单，只能由其他人抢单。抢单成功后，更新客户状态，重新置为私有资源。	

### 保存顾问和客户的历史关系

​	顾问和客户的关系主要包含以下几种：正在跟进、3天未跟进、15天未成单、已成单，每一种状态的历史记录都需要保存在数据库中，用于对顾问进行绩效考核。

### 员工考勤

​	支持一键考勤，默认所有人签到，对于迟到等情况，可以在考勤记录中对其进行单个或批量的考勤记录修改。

​	对于迟到、旷课的学生，可以在学习记录中对其进行单个或批量的考勤记录修改。

### 记录员工成绩，用Highcharts图表展示绩效

​	员工可查看自己的绩效，还可以使用图表展示成绩的折线图。

### 权限管理（组件）

​	权限管理为单独的组件，整合在CRM系统中后，可以对员工进行权限管理，即为不同的角色分配不同的可访问的URL。

### 其他功能

- **搜索框**

  可在配置中设置显示搜索框，对记录进行精确或模糊搜索。

- **组合搜索**

  可将多个字段作为组合搜索的条件，对记录进行组合搜索，支持多选。

- **批量操作记录**

  可实现批量删除记录的功能，也可以添加其他批量操作。




## 四、技术点

### 1.参考Django源码，利用单例模式，对每张表进行封装和注册

​	通过导入模块的方式实例化了一个单例对象`site`，调用它的`register()`方法对每一张表进行了注册，其中利用`CrmConfig`类对表进行了封装，在以后对表的操作中最常用的就是`CrmConfig`实例化后的表对象。

### 2.在`CrmConfig`类中对每张表进行了路由分配，支持扩展

​	为之前注册在`site`对象中的每一张表都生成了列表、添加、编辑、删除四个基础URL，同样封装在`site`对象中，让所有表的URL有一个共同的前缀。在生成基础URL之外，还预留了钩子函数，用于自定义扩展表的URL。

### 3.对列表页面的视图函数中部分数据，进行了类的封装

​	在每张表的列表页面的视图函数中，由于需要向模板传递的数据太多，所以使用类对数据进行了封装，**在向模板中传递数据时，只需实例化一个对象传入模板，在模板中调用方法就可以获取相应的数据。**其中主要包括以下4个功能：

- **获取批量操作的函数和描述信息**

  ​	每个批量操作需要对应一个函数，以及使用`short_desc`属性为函数添加描述。在获取到每一个批量操作的函数的信息后，对其进行封装，写在一个列表里，用于在模板中遍历生成`<select>`框中的`<option>`选项。

- **生成表格表头信息**

  ​	从设置的`list_display`属性中获取每一个要展示的字段对应的字段名或函数名，根据不同类型，选择调用Django原生方法显示字段的别名，或调用自定义函数返回设置好的别名，***使用生成器返回数据，优化性能***。

- **生成表格主体数据**

  ​	与表头相同，从设置的`list_distplay`属性中获取每一个要展示的字段对应的字段名或函数名，根据不同的类	型，选择返回字段内容或对应函数的返回值。

  ​	其中，***如果该字段在`list_editable`属性中存在***，需要将其转换为`<a>`标签链接到编辑页面。为了在编辑完成后还能返回当面页面，即保留当面URL中的参数和搜索条件，用到了Django原生的`QueryDict`类型，通过对其设置`mutable=True`，以及使用`urlencode()`方法，将URL中的参数和条件进行了封装，并拼接到了`<a>`标签的`href`中。

- **生成组合搜索条件**

  ​	在组合搜索中，每一行的搜索条件，应由当前页面记录的Foreign字段或Choice字段关联的内容生成。为此，借由在配置中***对字段进行类封装***的方法，为用于生成搜索行的字段添加了若干条件，实现了不同的功能，如：设置多选，标明是否是Choice类型字段，以及指定***生成`<a>`标签时拼接条件的值对应的字段***。

  ​	对于最后一个功能，说明一下，组合搜索的基本原理是点击`<a>`标签跳转到指定的URL，URL中的参数用于在数据库中进行筛选，所以参数的格式可能是`gender=1`或`role=3`这样，1和3为关联的记录的**主键**。但如果记录对象关联该字段时，用的不是主键，那URL中要求的参数可能是这样的：`department=1002`，这个地方的1002就不是主键字段的内容，所以在封装对象的时候，可以借由传入一个函数的方式来实现从指定字段取值。

### 4.使用`ModelForm`为每张表的添加、编辑页面生成标签

​	由于每张表的字段不同，在生成添加、编辑页面时，可以用`ModelForm`动态生成字段对应的标签。

### 5.使用type动态创建`ModelForm`类

​	因为`ModelForm`要关联到具体的表，而每张表又各不相同，所以用type实现动态创建`ModelForm`类。如果对字段、标签样式、错误信息有其他要求，可以单独写一个`ModelForm`类

### 6.前端渲染表格时，使用自定义方法来控制显示内容

​	在前端渲染表格时，添加、编辑按钮是可以多个表共用一个方法生成的，只需要对其返回值进行不同的拼接。但是每张表又有不同的字段，每个不同字段的显示内容也可能有不同的要求，所以在每张表的**配置类**（`CrmConfig`的派生类）中支持自定义方法，控制每个字段的显示内容。

### 7.使用Redis进行数据分发