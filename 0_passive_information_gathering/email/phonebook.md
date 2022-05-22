# phonebook.py

这是一个 recon-ng 的插件, 如果想单独跑, 只留业务相关代码就可. 对我来说recon-ng扩展性不错, 使用体验接近msf, 就用着了

## 使用在recon-ng:

1. 下载脚本后放到 `~/.recon-ng/modules/recon/domains-contacts` 目录
2. 启用 recon-ng 后搜索一下, 看看有没有成功加载
```bash
[recon-ng][default] > modules search phonebook
[*] Searching installed modules for 'phonebook'...

  Recon
  -----
    recon/domains-contacts/phonebook
```

3. 加载模块, 看到前面的提示符多了 [phonebook], 即表示成功加载
```bash
[recon-ng][default] > modules load recon/domains-contacts/phonebook
[recon-ng][default][phonebook] > 
```

4. 查看并配置运行参数, 这里跟msf差不多
```bash
[recon-ng][default][phonebook] > options list

  Name    Current Value  Required  Description
  ------  -------------  --------  -----------
  COUNT   10000          yes       Limit the amount of results returned. (10000 default)
  SOURCE  tencent.com    yes       source of input (see 'info' for details)

[recon-ng][default][phonebook] > options set SOURCE chaitin.com
SOURCE => chaitin.com
```

5. run
```bash
[recon-ng][default][phonebook] > run
[*] searching chaitin.com by phonebook
[*] api_url='https://public.intelx.io/', api_key='077424c6-7a26-410e-9269-c9ac546886a4'
[*] url='https://public.intelx.io/phonebook/search?k=077424c6-7a26-410e-9269-c9ac546886a4', data='{"term": "chaitin.com", "maxresults": 10000, "media": 0, "target": 2, "terminate": [], "timeout": 20}'
[*] request_id='cb3d06e5-aa49-4d92-8303-b96d72bddb8b'
[*] get response, url='https://public.intelx.io/phonebook/search/result?k=077424c6-7a26-410e-9269-c9ac546886a4&id=cb3d06e5-aa49-4d92-8303-b96d72bddb8b&limit=10000'
[*] got 11 emails
[*] Country: 
[*] Email: yang.li@chaitin.com
[*] First_Name: 
[*] Last_Name: 
[*] Middle_Name: None
[*] Notes: None
[*] Phone: None
[*] Region: 
[*] Title: None
[*] --------------------------------------------------
[*] Country: 
[*] Email: shengyu.zhang@chaitin.com
[*] First_Name: 
[*] Last_Name: 
[*] Middle_Name: None
[*] Notes: None
[*] Phone: None
[*] Region: 
[*] Title: None
[*] --------------------------------------------------

...

-------
SUMMARY
-------
[*] 11 total (11 new) contacts found.
```