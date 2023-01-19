# -*- coding: utf-8 -*-
# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
# AmosERP odoo11.0
# QQ:35350428
# 邮件:35350428@qq.com
# 手机：13584935775
# 作者：'amos'
# 公司网址： www.odoo.pw  www.100china.cn www.100china.cn
# Copyright 昆山一百计算机有限公司 2012-2018 Amos
# 日期：2018/09/12 15:01
# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

from dtcloud import api, fields, models, tools, SUPERUSER_ID, _


class global_search(models.Model):
    _name = "global.search"
    _description = u"全局搜索"

    name = fields.Char(string='名称')
    partner_id = fields.Many2one('res.partner', '业务伙伴')
    barcode = fields.Char(string='单号')
    partner_ref = fields.Char(string='对方单号')
    note = fields.Text('备注')
    action = fields.Integer(string='窗口', default=0)
    menu_id = fields.Integer(string='菜单', default=0)
    res_id = fields.Integer(string='单据ID')
    res_model = fields.Char(string='对象')
    url = fields.Char(string='URL地址')
    company_id = fields.Many2one('res.company', '公司', required=True,default=lambda s: s.env.company.id, index=True)
    partner_ids = fields.Many2many('res.partner', 'global_search_usrs_rel', 'search_id', 'user_id',string='查自己的单据')




    @api.model
    def _select_objects(self):
        records = self.env['ir.model'].search([])
        return [(record.model, record.name) for record in records] + [('', '')]

    id_object = fields.Reference(string='内部参考', selection='_select_objects')

    def button_open(self):
        self.ensure_one()
        id = self.id_object.id
        model = self.id_object._name
        client_action = {'type': 'ir.actions.act_url',
                         'name': u"查询",
                         'target': 'new',
                         'nodestroy': True,
                         'url': '/desk/view?id=%s&&table=%s&menu_id=%s' % (id, model, self.menu_id),
                         }
        return client_action

    def global_search_keyword(self):
        """
        前端字典查询
        :return:
        """
        context = dict(self._context or {})
        search = []
        if context.get('keyword'):
            if context.get('keyword') != '':
                keyword = context['keyword']
                domain = [('barcode', 'ilike', keyword)]
                search_row = self.search(domain, order="id desc", limit=10)

                for line in search_row:
                    description = ''
                    if line.id_object:
                        description = line.id_object._description
                    values = {
                        'id': line.id,
                        'name': line.name,
                        'partner_id': line.partner_id.name or '',
                        'barcode': line.barcode,
                        'partner_ref': line.partner_ref,
                        'note': line.note,
                        'action': line.action,
                        'menu_id': line.menu_id,
                        'res_id': line.res_id,
                        'res_model': line.res_model,
                        'url': line.url,
                        'id_object': line.id_object,
                        'description': description,
                    }
                    search.append(values)
        return search

class res_users(models.Model):
    _inherit = 'res.users'


    def s(self,line,context,name,barcode,note):
        #::::需要一个菜单全局事件id
        if context.get('global_search_men'):
            #:::::如果创建有编号就提交到查询库 开始
            domain = [('barcode', '=', line.name), ('res_model', '=', line._name)]
            search = self.env['global.search'].sudo().search(domain)
            if search:
                search.unlink()
            url = '/web#id=%s&action=%s&model=%s&view_type=form&menu_id=%s' % (
                line.id, context['global_search_actions'],line._name, context['global_search_men'])
            values = {
                'name': name,
                # 'partner_id': line.partner_id.id,
                'barcode': barcode,
                'res_id': line.id,
                'res_model': line._name,
                'url': url,
                'note': note,
                'company_id': line.company_id.id,
                'id_object': '%s,%s' % (line._name, line.id),
            }
            self.env['global.search'].sudo().create(values)
            return url
            #:::::如果创建有编号就提交到查询库 结束