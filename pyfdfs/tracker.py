# coding=utf-8
from __future__ import absolute_import

__author__ = 'mazesoul'

from pyfdfs.command import CommandHeader, Command
from pyfdfs.structs import StorageInfo, GroupInfo, BasicStorageInfo
from pyfdfs.enums import FDFS_GROUP_NAME_MAX_LEN, IP_ADDRESS_SIZE, \
    TRACKER_PROTO_CMD_SERVER_LIST_STORAGE, TRACKER_PROTO_CMD_SERVER_LIST_ALL_GROUPS, \
    TRACKER_PROTO_CMD_SERVER_LIST_ONE_GROUP, TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITHOUT_GROUP_ONE, \
    TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITH_GROUP_ONE, TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITHOUT_GROUP_ALL, \
    TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITH_GROUP_ALL, TRACKER_PROTO_CMD_SERVICE_QUERY_FETCH_ONE, \
    TRACKER_PROTO_CMD_SERVICE_QUERY_FETCH_ALL, TRACKER_PROTO_PKG_LEN_SIZE


class Tracker(object):
    def __init__(self, pool):
        self.pool = pool

    def list_groups(self):
        """
        :return: List<GroupInfo>

        * TRACKER_PROTO_CMD_SERVER_LIST_GROUP
           # function: list all groups
           # request body: none
           # response body: List<GroupInfo>
        """
        header = CommandHeader(cmd=TRACKER_PROTO_CMD_SERVER_LIST_ALL_GROUPS)
        cmd = Command(pool=self.pool, header=header)
        return cmd.fetch_list(GroupInfo)

    def list_one_group(self, group_name):
        """
        :param: group_name: which group
        :return: GroupInfo

        * TRACKER_PROTO_CMD_SERVER_LIST_ONE_GROUP
           # function: get one group info
           # request body:
              @ FDFS_GROUP_NAME_MAX_LEN bytes: the group name to query
           # response body: GroupInfo
        """
        header = CommandHeader(req_pkg_len=FDFS_GROUP_NAME_MAX_LEN, cmd=TRACKER_PROTO_CMD_SERVER_LIST_ONE_GROUP)
        cmd = Command(pool=self.pool, header=header, fmt='!%ds' % FDFS_GROUP_NAME_MAX_LEN)
        cmd.pack(group_name)
        return cmd.fetch_one(GroupInfo)

    def list_servers(self, group_name, storage_ip=None):
        """
        :param: group_name: which group
        :param: storage_ip: which storage servers
        :return: List<StorageInfo>

        * TRACKER_PROTO_CMD_SERVER_LIST_STORAGE
           # function: list storage servers of a group
           # request body:
              @ FDFS_GROUP_NAME_MAX_LEN bytes: the group name to
              @ IP_ADDRESS_SIZE bytes: this storage server ip address
           # response body: List<StorageInfo>
        """
        ip_len = IP_ADDRESS_SIZE if storage_ip else 0
        header = CommandHeader(req_pkg_len=FDFS_GROUP_NAME_MAX_LEN + ip_len, cmd=TRACKER_PROTO_CMD_SERVER_LIST_STORAGE)
        cmd = Command(pool=self.pool, header=header, fmt="!%ds %ds" % (FDFS_GROUP_NAME_MAX_LEN, ip_len))
        cmd.pack(group_name, storage_ip or "")
        return cmd.fetch_list(StorageInfo)

    def query_store_without_group_one(self):
        """
        :return: BasicStorageInfo

        * TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITHOUT_GROUP_ONE
           # function: query storage server for upload, without group name
           # request body: none (no body part)
           # response body: BasicStorageInfo
        """
        header = CommandHeader(cmd=TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITHOUT_GROUP_ONE)
        cmd = Command(pool=self.pool, header=header)
        return cmd.fetch_one(BasicStorageInfo)

    def query_store_with_group_one(self, group_name):
        """
        :param: group_name: which group
        :return: BasicStorageInfo

        * TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITH_GROUP_ONE
           # function: query storage server for upload, with group name
           # request body:
              @ FDFS_GROUP_NAME_MAX_LEN bytes: the group name to
           # response body: BasicStorageInfo
        """
        header = CommandHeader(req_pkg_len=FDFS_GROUP_NAME_MAX_LEN,
                               cmd=TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITH_GROUP_ONE)
        cmd = Command(pool=self.pool, header=header, fmt='!%ds' % FDFS_GROUP_NAME_MAX_LEN)
        cmd.pack(group_name)
        return cmd.fetch_one(BasicStorageInfo)

    def query_store_without_group_all(self):
        """
        :return: List<BasicStorageInfo>

        * TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITHOUT_GROUP_ALL
           # function: query which storage server to store file
           # request body: none (no body part)
           # response body: List<BasicStorageInfo>
        """
        header = CommandHeader(cmd=TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITHOUT_GROUP_ALL)
        cmd = Command(pool=self.pool, header=header)
        resp, resp_size = cmd.execute()
        server_count = (resp_size - FDFS_GROUP_NAME_MAX_LEN) / (IP_ADDRESS_SIZE + TRACKER_PROTO_PKG_LEN_SIZE)
        recv_fmt = '!%ds %ds %dQ B' % (FDFS_GROUP_NAME_MAX_LEN, server_count * IP_ADDRESS_SIZE, server_count)
        result = cmd.unpack(recv_fmt, resp)

        group_name = result[0]
        current_write_path = result[-1]
        si_list = []
        for idx in xrange(server_count):
            si = BasicStorageInfo()
            si.group_name = group_name
            si.current_write_path = current_write_path
            si.ip_addr = result[idx + 1]
            si.port = result[idx + 1 + server_count]
            si_list.append(si)
        return si_list

    def query_store_with_group_all(self, group_name):
        """
        :param group_name: which group
        :return: List<BasicStorageInfo>

        * TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITH_GROUP_ALL
           # function: query which storage server to store file, with group name
           # request body:
              @ FDFS_GROUP_NAME_MAX_LEN bytes: the group name to
           # response body: List<BasicStorageInfo>
        """
        header = CommandHeader(req_pkg_len=FDFS_GROUP_NAME_MAX_LEN,
                               cmd=TRACKER_PROTO_CMD_SERVICE_QUERY_STORE_WITH_GROUP_ALL)
        cmd = Command(pool=self.pool, header=header, fmt='!%ds' % FDFS_GROUP_NAME_MAX_LEN)
        cmd.pack(group_name)
        resp, resp_size = cmd.execute()
        server_count = (resp_size - FDFS_GROUP_NAME_MAX_LEN) / (IP_ADDRESS_SIZE + TRACKER_PROTO_PKG_LEN_SIZE)
        recv_fmt = '!%ds %ds %dQ B' % (FDFS_GROUP_NAME_MAX_LEN, server_count * IP_ADDRESS_SIZE, server_count)
        result = cmd.unpack(recv_fmt, resp)

        group_name = result[0]
        current_write_path = result[-1]
        si_list = []
        for idx in xrange(server_count):
            si = BasicStorageInfo()
            si.group_name = group_name
            si.current_write_path = current_write_path
            si.ip_addr = result[idx + 1]
            si.port = result[idx + 1 + server_count]
            si_list.append(si)
        return si_list

    def query_fetch_one(self, group_name, file_name):
        """
        :param group_name: which group
        :param file_name: which file
        :return: BasicStorageInfo

        * TRACKER_PROTO_CMD_SERVICE_QUERY_FETCH
           # function: query which storage server to download the file
           # request body:
              @ FDFS_GROUP_NAME_MAX_LEN bytes: group name
           # response body: BasicStorageInfo
        """
        file_name_size = len(file_name)
        header = CommandHeader(req_pkg_len=FDFS_GROUP_NAME_MAX_LEN + file_name_size,
                               cmd=TRACKER_PROTO_CMD_SERVICE_QUERY_FETCH_ONE)
        cmd = Command(pool=self.pool, header=header, fmt="!%ds %ds" % (FDFS_GROUP_NAME_MAX_LEN, file_name_size))
        recv_fmt = '!%ds %ds Q' % (FDFS_GROUP_NAME_MAX_LEN, IP_ADDRESS_SIZE)
        cmd.pack(group_name, file_name)
        si = BasicStorageInfo()
        si.group_name, si.ip_addr, si.port = cmd.fetch_by_fmt(recv_fmt)
        return si

    def query_fetch_all(self, group_name, file_name):
        """
        :param group_name: which group
        :param file_name: which file
        :return: List<BasicStorageInfo>

        * TRACKER_PROTO_CMD_SERVICE_QUERY_FETCH_ALL
           # function: query all storage servers to download the file
           # request body:
              @ FDFS_GROUP_NAME_MAX_LEN bytes: group name
              @ filename bytes: filename
           # response body: List<BasicStorageInfo>
        """
        file_name_size = len(file_name)
        header = CommandHeader(req_pkg_len=FDFS_GROUP_NAME_MAX_LEN + file_name_size,
                               cmd=TRACKER_PROTO_CMD_SERVICE_QUERY_FETCH_ALL)
        cmd = Command(pool=self.pool, header=header, fmt="!%ds %ds" % (FDFS_GROUP_NAME_MAX_LEN, file_name_size))
        cmd.pack(group_name, file_name)
        resp, resp_size = cmd.execute()
        server_count = (resp_size - FDFS_GROUP_NAME_MAX_LEN - 1 - TRACKER_PROTO_PKG_LEN_SIZE
                        - IP_ADDRESS_SIZE) / IP_ADDRESS_SIZE
        recv_fmt = '!%ds %ds Q %ds' % (FDFS_GROUP_NAME_MAX_LEN,
                                       IP_ADDRESS_SIZE,
                                       server_count * IP_ADDRESS_SIZE)
        result = cmd.unpack(recv_fmt, resp)
        group_name = result[0]
        server_port = result[2]
        si_list = []
        si = BasicStorageInfo()
        si.group_name = group_name
        si.ip_addr = result[1]
        si.port = server_port
        si_list.append(si)
        for idx in xrange(server_count):
            si = BasicStorageInfo()
            si.group_name = group_name
            si.ip_addr = result[idx + 3]
            si.port = server_port
            si_list.append(si)
        return si_list
